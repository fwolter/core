/******************************************************************************
  SD Card (SPI) Driver Interface Implementation

  Company:
    Microchip Technology Inc.

  File Name:
    drv_sdspi_plib_interface.c

  Summary:
    SD Card (SPI) Driver PLIB Interface implementation

  Description:
    This interface file segregates the SD Card SPI protocol from the underlying
    hardware layer implementation for SPI and Timer System service
*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
 *******************************************************************************/
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Include Files
// *****************************************************************************
// *****************************************************************************

#include <string.h>
#include "drv_sdspi_plib_interface.h"
<#if core.PRODUCT_FAMILY?matches("PIC32M.*") == false>
<#if core.DMA_ENABLE?has_content && drv_sdspi.DRV_SDSPI_SYS_DMA_ENABLE == true>
<#if core.DATA_CACHE_ENABLE?? && core.DATA_CACHE_ENABLE == true >
#include "system/cache/sys_cache.h"
</#if>
</#if>
</#if>

// *****************************************************************************
/* Timer Event Handler

  Summary:
    Event handler registered by the SD card driver with the Timer System Service

  Description:
    This event handler is called by the Timer System Service when the requested
    time period has elapsed.

  Remarks:

*/

static void DRV_SDSPI_TimerCallback( uintptr_t context )
{
    bool *flag = (bool *)context;
    *flag = true;
}

// *****************************************************************************
/* SDSPI SPI PLIB Event Handler

  Summary:
    Event handler registered by the SD card driver with the SPI PLIB

  Description:
    This event handler is called by the SPI PLIB when a request is complete

  Remarks:
    Block transfers always block on a semaphore in an RTOS environment. This
    semaphore is released from this callback when DMA is not used.

*/

void _DRV_SDSPI_SPIPlibCallbackHandler( uintptr_t context )
{
    DRV_SDSPI_OBJ* dObj = (DRV_SDSPI_OBJ *)context;

    dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_COMPLETE;

    SYS_PORT_PinSet(dObj->chipSelectPin);
}

<#if core.DMA_ENABLE?has_content && drv_sdspi.DRV_SDSPI_SYS_DMA_ENABLE == true>
<#if core.PRODUCT_FAMILY?matches("PIC32M.*") == true>
// *****************************************************************************
/* SDSPI RX DMA Event Handler

  Summary:
    Event handler registered by the SD card driver with the DMA System service
    for the receive DMA channel

  Description:
    This event handler is called by the DMA System Service when a DMA transfer
    is complete.

  Remarks:
    Block transfers always block on a semaphore in an RTOS environment. This
    semaphore is released from this callback when DMA is used.

*/

void _DRV_SDSPI_RX_DMA_CallbackHandler(
    SYS_DMA_TRANSFER_EVENT event,
    uintptr_t context
)
{
    uint32_t index;
    uint32_t size;
    DRV_SDSPI_OBJ* dObj = (DRV_SDSPI_OBJ *)context;

    if(event == SYS_DMA_TRANSFER_COMPLETE)
    {
        if (dObj->rxPending > 0)
        {
            /* txPending is 0. Need to use the dummy data buffer for transmission.
             * Find out the max data that can be received, given the limited size of the dummy data buffer.
             */
            (dObj->rxPending > DMA_DUMMY_BUFFER_SIZE) ?
                (size = DMA_DUMMY_BUFFER_SIZE): (size = dObj->rxPending);

            index = dObj->nBytesTransferred;

            /* Calculate the remaining rx bytes and total bytes transferred */
            dObj->rxPending -= size;
            dObj->nBytesTransferred += size;

            /* Always set up the rx channel first */
            SYS_DMA_ChannelTransfer(
                dObj->rxDMAChannel,
                (const void*)dObj->rxAddress,
                (const void *)&((uint8_t*)dObj->pReceiveData)[index],
                size
            );

            SYS_DMA_ChannelTransfer(
                dObj->txDMAChannel,
                (const void *)dObj->pDummyDataBuffer,
                (const void*)dObj->txAddress,
                size
            );
        }
        else if (dObj->txPending > 0)
        {
            /* rxPending is 0. Need to use the dummy data buffer for reception.
             * Find out the max data that can be transmitted, given the limited size of the dummy data buffer.
             */
            (dObj->txPending > DMA_DUMMY_BUFFER_SIZE) ?
                (size = DMA_DUMMY_BUFFER_SIZE): (size = dObj->txPending);

            index = dObj->nBytesTransferred;

            /* Calculate the remaining tx bytes and total bytes transferred */
            dObj->txPending -= size;
            dObj->nBytesTransferred += size;

            /* Always set up the rx channel first */
            SYS_DMA_ChannelTransfer(
                dObj->rxDMAChannel,
                (const void*)dObj->rxAddress,
                (const void *)dObj->pDummyDataBuffer,
                size
            );

            SYS_DMA_ChannelTransfer(
                dObj->txDMAChannel,
                (const void *)&((uint8_t*)dObj->pTransmitData)[index],
                (const void*)dObj->txAddress,
                size
            );
        }
        else
        {
            dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_COMPLETE;
            /* Make sure that the last byte is shifted out before CS is de-asserted */
            while (dObj->spiPlib->isTransmitterBusy());
            SYS_PORT_PinSet(dObj->chipSelectPin);
        }
    }
    else
    {
        dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_ERROR;
        /* Make sure that the last byte is shifted out before CS is de-asserted */
        while (dObj->spiPlib->isTransmitterBusy());
        SYS_PORT_PinSet(dObj->chipSelectPin);
    }
}

// *****************************************************************************
/* SDSPI TX DMA Event Handler

  Summary:
    Event handler registered by the SD card driver with the DMA System service
    for the transmit DMA channel

  Description:

  Remarks:

*/

void _DRV_SDSPI_TX_DMA_CallbackHandler(
    SYS_DMA_TRANSFER_EVENT event,
    uintptr_t context
)
{
    /* Do nothing */
}

// *****************************************************************************
/* SDSPI DMA Write

  Summary:
    Configures transmit and receive DMA channels for a write operation and starts
    the DMA transfer.

  Description:

  Remarks:

*/

static bool _DRV_SDSPI_DMA_Write(
    DRV_SDSPI_OBJ* dObj,
    void* pWriteBuffer,
    uint32_t nBytes
)
{
    uint32_t size;

    dObj->pTransmitData = pWriteBuffer;
    dObj->pReceiveData = NULL;
    dObj->txPending = nBytes;
    dObj->rxPending = 0;

    dObj->nBytesTransferred = 0;

    /* Initialize the dummy data buffer with 0xFF */
    memset(dObj->pDummyDataBuffer, 0xFF, DMA_DUMMY_BUFFER_SIZE);

    /* Need to use the dummy data buffer for reception.
     * Find out the max data that can be transmitted, given the limited size of the dummy data buffer.
     */
    (dObj->txPending > DMA_DUMMY_BUFFER_SIZE) ?
        (size = DMA_DUMMY_BUFFER_SIZE): (size = dObj->txPending);

    /* Calculate the remaining tx bytes and total bytes transferred */
    dObj->txPending -= size;
    dObj->nBytesTransferred += size;

    /* Always set up the rx channel first */
    SYS_DMA_ChannelTransfer(
        dObj->rxDMAChannel,
        (const void*)dObj->rxAddress,
        (const void *)dObj->pDummyDataBuffer,
        size
    );

    SYS_DMA_ChannelTransfer(
        dObj->txDMAChannel,
        (const void *)pWriteBuffer,
        (const void*)dObj->txAddress,
        size
    );

    return true;
}

// *****************************************************************************
/* SDSPI DMA Read

  Summary:
    Configures the transmit and receive DMA channels for a read operation and starts
    the DMA transfer.

  Description:

  Remarks:

*/

static bool _DRV_SDSPI_DMA_Read(
    DRV_SDSPI_OBJ* dObj,
    void* pReadBuffer,
    uint32_t nBytes
)
{
    uint32_t size;

    dObj->pReceiveData = pReadBuffer;
    dObj->pTransmitData = NULL;
    dObj->rxPending = nBytes;
    dObj->txPending = 0;
    dObj->nBytesTransferred = 0;

    /* Initialize the dummy data buffer with 0xFF */
    memset(dObj->pDummyDataBuffer, 0xFF, DMA_DUMMY_BUFFER_SIZE);

    /* Need to use the dummy data buffer for transmission.
     * Find out the max data that can be received, given the limited size of the dummy data buffer.
     */
    (dObj->rxPending > DMA_DUMMY_BUFFER_SIZE) ?
        (size = DMA_DUMMY_BUFFER_SIZE): (size = dObj->rxPending);

    /* Calculate the remaining rx bytes and total bytes transferred */
    dObj->rxPending -= size;
    dObj->nBytesTransferred += size;

    /* Always set up the rx channel first */
    SYS_DMA_ChannelTransfer(
        dObj->rxDMAChannel,
        (const void*)dObj->rxAddress,
        (const void *)pReadBuffer,
        size
    );

    SYS_DMA_ChannelTransfer(
        dObj->txDMAChannel,
        (const void *)dObj->pDummyDataBuffer,
        (const void*)dObj->txAddress,
        size
    );

    return true;
}
<#else>
// *****************************************************************************
/* SDSPI RX DMA Event Handler

  Summary:
    Event handler registered by the SD card driver with the DMA System service
    for the receive DMA channel

  Description:
    This event handler is called by the DMA System Service when a DMA transfer
    is complete.

  Remarks:
    Block transfers always block on a semaphore in an RTOS environment. This
    semaphore is released from this callback when DMA is used.

*/

void _DRV_SDSPI_RX_DMA_CallbackHandler(
    SYS_DMA_TRANSFER_EVENT event,
    uintptr_t context
)
{
    DRV_SDSPI_OBJ* dObj = (DRV_SDSPI_OBJ *)context;

    if(event == SYS_DMA_TRANSFER_COMPLETE)
    {
        dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_COMPLETE;
    }
    else
    {
        dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_ERROR;
    }

    /* Make sure that the last byte is shifted out before CS is de-asserted */
    while (dObj->spiPlib->isTransmitterBusy());
    SYS_PORT_PinSet(dObj->chipSelectPin);
}

// *****************************************************************************
/* SDSPI TX DMA Event Handler

  Summary:
    Event handler registered by the SD card driver with the DMA System service
    for the transmit DMA channel

  Description:

  Remarks:

*/

void _DRV_SDSPI_TX_DMA_CallbackHandler(
    SYS_DMA_TRANSFER_EVENT event,
    uintptr_t context
)
{
    /* Do nothing */
}


// *****************************************************************************
/* SDSPI DMA Write

  Summary:
    Configures transmit and receive DMA channels for a write operation and starts
    the DMA transfer.

  Description:

  Remarks:

*/

static bool _DRV_SDSPI_DMA_Write(
    DRV_SDSPI_OBJ* dObj,
    void* pWriteBuffer,
    uint32_t nBytes
)
{
<#if core.DATA_CACHE_ENABLE?? && core.DATA_CACHE_ENABLE == true >
    /* Clean cache to flush the data from the cache to the main memory */
    SYS_CACHE_CleanDCache_by_Addr (pWriteBuffer, nBytes);
</#if>

    /* Setup DMA Receive channel to receive dummy data */
    SYS_DMA_AddressingModeSetup(
        dObj->rxDMAChannel,
        SYS_DMA_SOURCE_ADDRESSING_MODE_FIXED,
        SYS_DMA_DESTINATION_ADDRESSING_MODE_FIXED
    );

    SYS_DMA_ChannelTransfer(
        dObj->rxDMAChannel,
        (const void *)dObj->rxAddress,      /* Source Address */
        (const void*)&dObj->rxDummyData,    /* Destination Address */
        nBytes
    );

    /* Setup DMA Transmit channel to transmit the write buffer */
    SYS_DMA_AddressingModeSetup(
        dObj->txDMAChannel,
        SYS_DMA_SOURCE_ADDRESSING_MODE_INCREMENTED,
        SYS_DMA_DESTINATION_ADDRESSING_MODE_FIXED
    );

    SYS_DMA_ChannelTransfer(
        dObj->txDMAChannel,
        (const void *)pWriteBuffer,         /* Source Address */
        (const void*)dObj->txAddress,       /* Destination Address */
        nBytes
    );

    return true;
}

// *****************************************************************************
/* SDSPI DMA Read

  Summary:
    Configures the transmit and receive DMA channels for a read operation and starts
    the DMA transfer.

  Description:

  Remarks:

*/

static bool _DRV_SDSPI_DMA_Read(
    DRV_SDSPI_OBJ* dObj,
    void* pReadBuffer,
    uint32_t nBytes
)
{
    /* Setup the DMA Receive channel to receive data into the read buffer */

<#if core.DATA_CACHE_ENABLE?? && core.DATA_CACHE_ENABLE == true >
    /* Invalidate cache to force CPU to read from the main memory */
    SYS_CACHE_InvalidateDCache_by_Addr(pReadBuffer, nBytes);
</#if>

    SYS_DMA_AddressingModeSetup(
        dObj->rxDMAChannel,
        SYS_DMA_SOURCE_ADDRESSING_MODE_FIXED,
        SYS_DMA_DESTINATION_ADDRESSING_MODE_INCREMENTED
    );

    SYS_DMA_ChannelTransfer(
        dObj->rxDMAChannel,
        (const void *)dObj->rxAddress,      /* Source Address */
        (const void*)pReadBuffer,           /* Destination Address */
        nBytes
    );

    /* Setup the DMA Transmit channel to transmit dummy data */

    SYS_DMA_AddressingModeSetup(
        dObj->txDMAChannel,
        SYS_DMA_SOURCE_ADDRESSING_MODE_FIXED,
        SYS_DMA_DESTINATION_ADDRESSING_MODE_FIXED
    );

    SYS_DMA_ChannelTransfer(
        dObj->txDMAChannel,
        (const void *)dObj->txDummyData,        /* Source Address */
        (const void*)dObj->txAddress,           /* Destination Address */
        nBytes
    );

    return true;
}
</#if>
</#if>
// *****************************************************************************
/* SD Card SPI Write

  Summary:
    Writes the requested number of bytes to the SD Card

  Description:

  Remarks:
    This is a blocking implementation. This function does not block on a semaphore.
*/

bool _DRV_SDSPI_SPIWrite(
    DRV_SDSPI_OBJ* dObj,
    void* pWriteBuffer,
    uint32_t nBytes
)
{
    bool isSuccess = false;

    SYS_PORT_PinClear(dObj->chipSelectPin);

    dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_IN_PROGRESS;

<#if core.DMA_ENABLE?has_content && drv_sdspi.DRV_SDSPI_SYS_DMA_ENABLE == true>
    /* If enabled, used DMA */
    if ((dObj->txDMAChannel != SYS_DMA_CHANNEL_NONE) && (dObj->rxDMAChannel != SYS_DMA_CHANNEL_NONE ))
    {
        if (_DRV_SDSPI_DMA_Write(dObj, pWriteBuffer, nBytes) == false)
        {
            SYS_PORT_PinSet(dObj->chipSelectPin);
        }
        else
        {
            isSuccess = true;
        }
    }
    else
    {
        if (dObj->spiPlib->write (pWriteBuffer, nBytes) == false)
        {
            SYS_PORT_PinSet(dObj->chipSelectPin);
        }
        else
        {
            isSuccess = true;
        }
    }
<#else>
    if (dObj->spiPlib->write (pWriteBuffer, nBytes) == false)
    {
        SYS_PORT_PinSet(dObj->chipSelectPin);
    }
    else
    {
        isSuccess = true;
    }
</#if>

    return isSuccess;
}

// *****************************************************************************
/* SD Card SPI read

  Summary:
    Reads the requested number of bytes from the SD Card

  Description:

  Remarks:
    This is a blocking implementation. This function does not block on a semaphore.
*/

bool _DRV_SDSPI_SPIRead(
    DRV_SDSPI_OBJ* dObj,
    void* pReadBuffer,
    uint32_t nBytes
)
{
    bool isSuccess = false;

    SYS_PORT_PinClear(dObj->chipSelectPin);

    dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_IN_PROGRESS;

<#if core.DMA_ENABLE?has_content && drv_sdspi.DRV_SDSPI_SYS_DMA_ENABLE == true>
    /* If enabled, used DMA */
    if ((dObj->txDMAChannel != SYS_DMA_CHANNEL_NONE) && (dObj->rxDMAChannel != SYS_DMA_CHANNEL_NONE ))
    {
        if (_DRV_SDSPI_DMA_Read(dObj, pReadBuffer, nBytes) == false)
        {
            SYS_PORT_PinSet(dObj->chipSelectPin);
        }
        else
        {
            isSuccess = true;
        }
    }
    else
    {
        if (dObj->spiPlib->read (pReadBuffer, nBytes) == false)
        {
            SYS_PORT_PinSet(dObj->chipSelectPin);
        }
        else
        {
            isSuccess = true;
        }
    }
<#else>
    if (dObj->spiPlib->read (pReadBuffer, nBytes) == false)
    {
        SYS_PORT_PinSet(dObj->chipSelectPin);
    }
    else
    {
        isSuccess = true;
    }
</#if>

    return isSuccess;
}

bool _DRV_SDSPI_SPIWriteWithChipSelectDisabled(
    DRV_SDSPI_OBJ* dObj,
    void* pWriteBuffer,
    uint32_t nBytes
)
{
    bool isSuccess = false;

    SYS_PORT_PinSet(dObj->chipSelectPin);

    dObj->spiTransferStatus = DRV_SDSPI_SPI_TRANSFER_STATUS_IN_PROGRESS;

<#if core.DMA_ENABLE?has_content && drv_sdspi.DRV_SDSPI_SYS_DMA_ENABLE == true>
    /* If enabled, used DMA */
    if ((dObj->txDMAChannel != SYS_DMA_CHANNEL_NONE) && (dObj->rxDMAChannel != SYS_DMA_CHANNEL_NONE ))
    {
        if (_DRV_SDSPI_DMA_Write(dObj, pWriteBuffer, nBytes) == true)
        {
            isSuccess = true;
        }
    }
    else
    {
        if (dObj->spiPlib->write (pWriteBuffer, nBytes) == true)
        {
            isSuccess = true;
        }
    }
<#else>
    if (dObj->spiPlib->write (pWriteBuffer, nBytes) == true)
    {
        isSuccess = true;
    }
</#if>

    return isSuccess;
}

// *****************************************************************************
/* Card Insertion/Removal Polling Timer

  Summary:
    Registers an event handler with the Timer System Service and starts the
    command-response timer.

  Description:
    The registered event handler is called when the time period elapses.

  Remarks:

*/
bool _DRV_SDSPI_CardDetectPollingTimerStart(
    DRV_SDSPI_OBJ* const dObj,
    uint32_t period
)
{
    bool isSuccess = false;
    dObj->cardPollingTimerExpired = false;

    dObj->cardPollingTmrHandle = SYS_TIME_CallbackRegisterMS(DRV_SDSPI_TimerCallback,
             (uintptr_t)&dObj->cardPollingTimerExpired, period, SYS_TIME_SINGLE);

    if (dObj->cardPollingTmrHandle != SYS_TIME_HANDLE_INVALID)
    {
        isSuccess = true;
    }

    return isSuccess;
}

// *****************************************************************************
/* Command Response Timer Start

  Summary:
    Registers an event handler with the Timer System Service and starts the
    command-response timer.

  Description:
    The registered event handler is called when the time period elapses.

  Remarks:

*/
bool _DRV_SDSPI_CmdResponseTimerStart(
    DRV_SDSPI_OBJ* const dObj,
    uint32_t period
)
{
    bool isSuccess = false;
    dObj->cmdRespTmrExpired = false;

    dObj->cmdRespTmrHandle = SYS_TIME_CallbackRegisterMS(DRV_SDSPI_TimerCallback,
             (uintptr_t)&dObj->cmdRespTmrExpired, period, SYS_TIME_SINGLE);

    if (dObj->cmdRespTmrHandle != SYS_TIME_HANDLE_INVALID)
    {
        isSuccess = true;
    }

    return isSuccess;
}

// *****************************************************************************
/* Command Response Timer Stop

  Summary:
    Stops the command-response timer.

  Description:

  Remarks:

*/

bool _DRV_SDSPI_CmdResponseTimerStop( DRV_SDSPI_OBJ* const dObj )
{
    bool isSuccess = false;

    if (dObj->cmdRespTmrHandle != SYS_TIME_HANDLE_INVALID)
    {
        SYS_TIME_TimerDestroy(dObj->cmdRespTmrHandle);
        isSuccess = true;
    }

    return isSuccess;
}

// *****************************************************************************
/* SD Card Timer Start

  Summary:
    Starts the SD card timer.

  Description:
    The registered event handler is called when the time period elapses.

  Remarks:

*/

bool _DRV_SDSPI_TimerStart(
    DRV_SDSPI_OBJ* const dObj,
    uint32_t period
)
{
    bool isSuccess = false;
    dObj->timerExpired = false;

    dObj->timerHandle = SYS_TIME_CallbackRegisterMS(DRV_SDSPI_TimerCallback,
             (uintptr_t)&dObj->timerExpired, period, SYS_TIME_SINGLE);

    if (dObj->timerHandle != SYS_TIME_HANDLE_INVALID)
    {
        isSuccess = true;
    }

    return isSuccess;
}

// *****************************************************************************
/* SD Card Timer Stop

  Summary:
    Stops the SD card timer.

  Description:
    The registered event handler is called when the time period elapses.

  Remarks:

*/

bool _DRV_SDSPI_TimerStop( DRV_SDSPI_OBJ* const dObj )
{
    bool isSuccess = false;

    if (dObj->timerHandle != SYS_TIME_HANDLE_INVALID)
    {
        SYS_TIME_TimerDestroy(dObj->timerHandle);
        isSuccess = true;
    }

    return isSuccess;
}

// *****************************************************************************
/* SD Card SPI Speed Setup

  Summary:
    Configures the SPI clock frequency.

  Description:
    This function is used by the SD Card driver to switch between the initial
    low frequency and to higher clock frequency once the SD card is initialized.

  Remarks:

*/

bool _DRV_SDSPI_SPISpeedSetup(
    DRV_SDSPI_OBJ* const dObj,
    uint32_t clockFrequency
)
{
    bool isSuccess = false;
    DRV_SDSPI_TRANSFER_SETUP sdspiSetup;
    DRV_SDSPI_TRANSFER_SETUP setupRemap;

    /* SD Card reads the data on the rising edge of SCK, which means SPI Mode 0
     * and 3 => CPOL = 0, CPHA = 0 and CPOL = 1, CPHA = 1 are supported */

    sdspiSetup.baudRateInHz = clockFrequency;
    sdspiSetup.clockPhase = DRV_SDSPI_CLOCK_PHASE_VALID_LEADING_EDGE;
    sdspiSetup.clockPolarity = DRV_SDSPI_CLOCK_POLARITY_IDLE_LOW;
    sdspiSetup.dataBits = DRV_SDSPI_DATA_BITS_8;

    setupRemap = sdspiSetup;

    setupRemap.clockPolarity = (DRV_SDSPI_CLOCK_POLARITY)dObj->remapClockPolarity[sdspiSetup.clockPolarity];
    setupRemap.clockPhase = (DRV_SDSPI_CLOCK_PHASE)dObj->remapClockPhase[sdspiSetup.clockPhase];
    setupRemap.dataBits = (DRV_SDSPI_DATA_BITS)dObj->remapDataBits[sdspiSetup.dataBits];

    if ((setupRemap.clockPhase != DRV_SDSPI_CLOCK_PHASE_INVALID) &&
        (setupRemap.clockPolarity != DRV_SDSPI_CLOCK_POLARITY_INVALID) &&
        (setupRemap.dataBits != DRV_SDSPI_DATA_BITS_INVALID))
    {
        isSuccess = dObj->spiPlib->transferSetup(&setupRemap, 0);
    }

    return isSuccess;
}