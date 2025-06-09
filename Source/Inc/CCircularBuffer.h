#ifndef _CCIRCULAR_BUFFER_H_
#define _CCIRCULAR_BUFFER_H_

#include <ntddk.h>

class CCircularBuffer
{
private:
    PUCHAR m_Buffer;         // Pointer to circular buffer memory
    ULONG  m_Size;           // Total size of buffer
    ULONG  m_Head;           // Write pointer
    ULONG  m_Tail;           // Read pointer
    KSPIN_LOCK m_Lock;       // Spinlock for thread-safe access

public:
    CCircularBuffer();
    ~CCircularBuffer();

    NTSTATUS Initialize(ULONG size);
    NTSTATUS Write(PUCHAR data, ULONG length);
    NTSTATUS Read(PUCHAR outBuffer, ULONG length, ULONG* bytesRead, bool zeroPadIfInsufficient);
    ULONG FreeSpace() const;
    ULONG UsedSpace() const;
    void Reset();
};

#endif // _CCIRCULAR_BUFFER_H_
