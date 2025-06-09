#include "CCircularBuffer.h"

CCircularBuffer::CCircularBuffer() :
    m_Buffer(nullptr),
    m_Size(0),
    m_Head(0),
    m_Tail(0)
{
    KeInitializeSpinLock(&m_Lock);
}

CCircularBuffer::~CCircularBuffer()
{
    if (m_Buffer) {
        ExFreePoolWithTag(m_Buffer, 'BufA');
        m_Buffer = nullptr;
    }

    m_Size = 0;
    m_Head = 0;
    m_Tail = 0;
}

NTSTATUS CCircularBuffer::Initialize(ULONG size)
{
    if (size == 0) {
        return STATUS_INVALID_PARAMETER;
    }

    if (m_Buffer) {
        ExFreePoolWithTag(m_Buffer, 'BufA');
        m_Buffer = nullptr;
    }

    m_Buffer = (PUCHAR)ExAllocatePool2(POOL_FLAG_NON_PAGED, size, 'BufA');

    if (!m_Buffer) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    m_Size = size;
    m_Head = 0;
    m_Tail = 0;
    return STATUS_SUCCESS;
}

NTSTATUS CCircularBuffer::Write(PUCHAR data, ULONG length)
{
    if (!data || !m_Buffer || m_Size == 0) {
        return STATUS_INVALID_PARAMETER;
    }

    KIRQL oldIrql;
    KeAcquireSpinLock(&m_Lock, &oldIrql);

    if (FreeSpace() < length) {
        KeReleaseSpinLock(&m_Lock, oldIrql);
        return STATUS_BUFFER_OVERFLOW;
    }

    for (ULONG i = 0; i < length; ++i) {
        m_Buffer[m_Head] = data[i];
        m_Head = (m_Head + 1) % m_Size;
    }

    KeReleaseSpinLock(&m_Lock, oldIrql);
    return STATUS_SUCCESS;
}

NTSTATUS CCircularBuffer::Read(PUCHAR dest, ULONG length, PULONG bytesRead, bool zeroPadIfInsufficient)
{
    if (!dest || !m_Buffer || m_Size == 0 || !bytesRead) {
        return STATUS_INVALID_PARAMETER;
    }

    *bytesRead = 0;

    KIRQL oldIrql;
    KeAcquireSpinLock(&m_Lock, &oldIrql);

    ULONG available = (m_Head >= m_Tail)
        ? (m_Head - m_Tail)
        : (m_Size - m_Tail + m_Head);

    if (available == 0) {
        KeReleaseSpinLock(&m_Lock, oldIrql);
        return STATUS_NO_MORE_ENTRIES;
    }

    ULONG toRead = min(length, available);

    for (ULONG i = 0; i < toRead; ++i) {
        dest[i] = m_Buffer[m_Tail];
        m_Tail = (m_Tail + 1) % m_Size;
    }

    KeReleaseSpinLock(&m_Lock, oldIrql);

    *bytesRead = toRead;

    if (zeroPadIfInsufficient && toRead < length) {
        RtlZeroMemory(dest + toRead, length - toRead);
    }

    return STATUS_SUCCESS;
}


ULONG CCircularBuffer::FreeSpace() const
{
    if (!m_Buffer || m_Size == 0) {
        return 0;
    }

    if (m_Head >= m_Tail)
        return m_Size - (m_Head - m_Tail) - 1;
    else
        return (m_Tail - m_Head - 1);
}

ULONG CCircularBuffer::UsedSpace() const
{
    if (!m_Buffer || m_Size == 0) {
        return 0;
    }

    if (m_Head >= m_Tail)
        return m_Head - m_Tail;
    else
        return m_Size - (m_Tail - m_Head);
}

void CCircularBuffer::Reset()
{
    KIRQL oldIrql;
    KeAcquireSpinLock(&m_Lock, &oldIrql);

    m_Head = 0;
    m_Tail = 0;

    KeReleaseSpinLock(&m_Lock, oldIrql);
}