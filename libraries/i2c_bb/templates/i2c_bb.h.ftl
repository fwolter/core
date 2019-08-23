/*******************************************************************************
  I2C BIT BANG Library Interface Header File

  Company
    Microchip Technology Inc.

  File Name
    ${I2CBB_INSTANCE_NAME?lower_case}.h

  Summary
    I2CBB library interface.

  Description
    This file defines the interface to the I2CBB library.

  Remarks:

*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
* Copyright (C) 2018 Microchip Technology Inc. and its subsidiaries.
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

#ifndef ${I2CBB_INSTANCE_NAME}_H
#define ${I2CBB_INSTANCE_NAME}_H

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

/*  This section lists the other files that are included in this file.
*/
#include "i2c_bb_local.h"
// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    extern "C" {

#endif
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Data Types
// *****************************************************************************
// *****************************************************************************

// *****************************************************************************
// *****************************************************************************
// Section: Interface Routines
// *****************************************************************************
// *****************************************************************************
/* The following functions make up the methods (set of possible operations) of
   this interface.
*/

void ${I2CBB_INSTANCE_NAME}_Initialize(void);

void ${I2CBB_INSTANCE_NAME}_CallbackRegister(I2CBB_CALLBACK callback, uintptr_t contextHandle);

bool ${I2CBB_INSTANCE_NAME}_IsBusy(void);

bool ${I2CBB_INSTANCE_NAME}_Read(uint16_t address, uint8_t *pdata, size_t length);

bool ${I2CBB_INSTANCE_NAME}_Write(uint16_t address, uint8_t *pdata, size_t length);

bool ${I2CBB_INSTANCE_NAME}_WriteRead(uint16_t address, uint8_t *wdata, size_t wlength, uint8_t *rdata, size_t rlength);

I2CBB_ERROR ${I2CBB_INSTANCE_NAME}_ErrorGet(void);

bool ${I2CBB_INSTANCE_NAME}_TransferSetup(I2CBB_TRANSFER_SETUP* setup, uint32_t tmrSrcClkFreq );


// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    }

#endif
// DOM-IGNORE-END

#endif //${I2CBB_INSTANCE_NAME}_H

/*******************************************************************************
 End of File
*/