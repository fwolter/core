# coding: utf-8
"""*****************************************************************************
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
*****************************************************************************"""

################################################################################
#### Component ####
################################################################################

sdspiFsEnable = None

global isDMAPresent
global sort_alphanumeric

cardDetectMethodComboValues = ["Use Polling"]

def handleMessage(messageID, args):

    result_dict = {}

    if (messageID == "REQUEST_CONFIG_PARAMS"):
        if args.get("localComponentID") != None:
            result_dict = Database.sendMessage(args["localComponentID"], "SPI_MASTER_MODE", {"isReadOnly":True, "isEnabled":True})
            result_dict = Database.sendMessage(args["localComponentID"], "SPI_MASTER_INTERRUPT_MODE", {"isReadOnly":True, "isEnabled":True})
            result_dict = Database.sendMessage(args["localComponentID"], "SPI_MASTER_HARDWARE_CS", {"isReadOnly":True, "isEnabled":False})

    return result_dict

def sort_alphanumeric(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def setVisible(symbol, event):
    symbol.setVisible(event["value"])

def genRtosTask(symbol, event):
    if event["value"] != "BareMetal":
        symbol.setEnabled(True)
    else:
        symbol.setEnabled(False)

def showRTOSMenu(symbol, event):
    if event["value"] != "BareMetal":
        symbol.setVisible(True)
    else:
        symbol.setVisible(False)

def showWriteProtectComment(symbol, event):
    symbol.setVisible(event["value"])

def requestDMAComment(symbol, event):
    global sdspiTXRXDMA

    if ((event["value"] == -2) and (sdspiTXRXDMA.getValue() == True)):
        symbol.setVisible(True)
        event["symbol"].setVisible(False)
    else:
        symbol.setVisible(False)

def asyncModeOptions(symbol, event):
    if (event["value"] == "Asynchronous"):
        symbol.setVisible(True)
    else:
        symbol.setVisible(False)

def setPLIBOptionsVisibility(symbol, event):
    global isDMAPresent

    if (symbol.getID() == "DRV_SDSPI_TX_RX_DMA"):
        if (isDMAPresent == True):
            symbol.setVisible(event["value"] == "SPI_PLIB")
    else:
        symbol.setVisible(event["value"] == "SPI_PLIB")

def setDriverOptionsVisibility(symbol, event):
    symbol.setVisible(event["value"] == "SPI_DRV")

def requestAndAssignDMAChannel(symbol, event):
    global drvSdspiInstanceSpace

    spiPeripheral = Database.getSymbolValue(drvSdspiInstanceSpace, "DRV_SDSPI_PLIB")

    if symbol.getID() == "DRV_SDSPI_TX_DMA_CHANNEL":
        dmaChannelID = "DMA_CH_FOR_" + str(spiPeripheral) + "_Transmit"
        dmaRequestID = "DMA_CH_NEEDED_FOR_" + str(spiPeripheral) + "_Transmit"
    else:
        dmaChannelID = "DMA_CH_FOR_" + str(spiPeripheral) + "_Receive"
        dmaRequestID = "DMA_CH_NEEDED_FOR_" + str(spiPeripheral) + "_Receive"

    # Control visibility
    symbol.setVisible(event["value"])

    # Clear the DMA symbol. Done for backward compatibility.
    Database.clearSymbolValue("core", dmaRequestID)

    dummyDict = {}

    if event["value"] == False:
        dummyDict = Database.sendMessage("core", "DMA_CHANNEL_DISABLE", {"dma_channel":dmaRequestID})
    else:
        dummyDict = Database.sendMessage("core", "DMA_CHANNEL_ENABLE", {"dma_channel":dmaRequestID})

    # Get the allocated channel and assign it
    channel = Database.getSymbolValue("core", dmaChannelID)
    if channel != None:
        symbol.setValue(channel)

def sdspiRtosMicriumOSIIIAppTaskVisibility(symbol, event):
    if (event["value"] == "MicriumOSIII"):
        symbol.setVisible(True)
    else:
        symbol.setVisible(False)

def sdspiRtosMicriumOSIIITaskOptVisibility(symbol, event):
    symbol.setVisible(event["value"])

def getActiveRtos():
    activeComponents = Database.getActiveComponentIDs()

    for i in range(0, len(activeComponents)):
        if (activeComponents[i] == "FreeRTOS"):
            return "FreeRTOS"
        elif (activeComponents[i] == "ThreadX"):
            return "ThreadX"
        elif (activeComponents[i] == "MicriumOSIII"):
            return "MicriumOSIII"
        elif (activeComponents[i] == "MbedOS"):
            return "MbedOS"

def asyncFileGenration(symbol, event):
    global sdspiInterfaceType

    commonMode = Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE")
    interfaceType = sdspiInterfaceType.getValue()

    if(commonMode== "Synchronous"):
        symbol.setEnabled(False)
    else:
        if (symbol.getID() == "DRV_SDSPI_ASYNC_PLIB_INTERFACE_SOURCE"):
            if (interfaceType == "SPI_PLIB"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_ASYNC_DRIVER_INTERFACE_SOURCE"):
            if (interfaceType == "SPI_DRV"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_ASYNC_PLIB_INTERFACE_HEADER"):
            if (interfaceType == "SPI_PLIB"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_ASYNC_DRIVER_INTERFACE_HEADER"):
            if (interfaceType == "SPI_DRV"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        else:
            symbol.setEnabled(True)

def syncFileGenration(symbol, event):
    global sdspiInterfaceType

    commonMode = Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE")
    interfaceType = sdspiInterfaceType.getValue()

    if(commonMode == "Asynchronous"):
        symbol.setEnabled(False)
    else:
        if (symbol.getID() == "DRV_SDSPI_SYNC_PLIB_INTERFACE_SOURCE"):
            if (interfaceType == "SPI_PLIB"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_SYNC_DRIVER_INTERFACE_SOURCE"):
            if (interfaceType == "SPI_DRV"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_SYNC_PLIB_INTERFACE_HEADER"):
            if (interfaceType == "SPI_PLIB"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        elif (symbol.getID() == "DRV_SDSPI_SYNC_DRIVER_INTERFACE_HEADER"):
            if (interfaceType == "SPI_DRV"):
                symbol.setEnabled(True)
            else:
                symbol.setEnabled(False)
        else:
            symbol.setEnabled(True)

def updateDMAEnableCntr(symbol, event):
    result_dict = {}

    if symbol.getValue() != event["value"]:
        symbol.setValue(event["value"])
        if symbol.getValue() == True:
            result_dict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_DMA_ENABLED", result_dict)
        else:
            result_dict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_DMA_DISABLED", result_dict)

def instantiateComponent(sdspiComponent, index):
    global drvSdspiInstanceSpace
    global sdspiFsEnable
    global sdspiTXRXDMA
    global isDMAPresent
    global sdspiInterfaceType

    print "sdspiComponent = " + str(sdspiComponent.getID())

    drvSdspiInstanceSpace = "drv_sdspi_" + str(index)

    if Database.getSymbolValue("core", "DMA_ENABLE") == None:
        isDMAPresent = False
    else:
        isDMAPresent = True

    availablePinDictionary = {}

    availablePinDictionary = Database.sendMessage("core", "DRV_SDSPI", availablePinDictionary)

    sdspiSymIndex = sdspiComponent.createIntegerSymbol("INDEX", None)
    sdspiSymIndex.setVisible(False)
    sdspiSymIndex.setDefaultValue(index)

    sdspiInterfaceType = sdspiComponent.createStringSymbol("DRV_SDSPI_INTERFACE_TYPE", None)
    sdspiInterfaceType.setLabel("SDSPI Interface Type")
    sdspiInterfaceType.setVisible(False)
    sdspiInterfaceType.setDefaultValue("")

    sdspiSymPLIB = sdspiComponent.createStringSymbol("DRV_SDSPI_PLIB", None)
    sdspiSymPLIB.setLabel("PLIB Used")
    sdspiSymPLIB.setReadOnly(True)
    sdspiSymPLIB.setDefaultValue("")
    sdspiSymPLIB.setVisible(False)
    sdspiSymPLIB.setDependencies(setPLIBOptionsVisibility, ["DRV_SDSPI_INTERFACE_TYPE"])

    sdspiSymDrvInstance = sdspiComponent.createStringSymbol("DRV_SDSPI_SPI_DRIVER_INSTANCE", None)
    sdspiSymDrvInstance.setLabel("SPI Driver Instance Used")
    sdspiSymDrvInstance.setReadOnly(True)
    sdspiSymDrvInstance.setDefaultValue("")
    sdspiSymDrvInstance.setVisible(False)
    sdspiSymDrvInstance.setDependencies(setDriverOptionsVisibility, ["DRV_SDSPI_INTERFACE_TYPE"])

    sdspiSymNumClients = sdspiComponent.createIntegerSymbol("DRV_SDSPI_NUM_CLIENTS", None)
    sdspiSymNumClients.setLabel("Number of Clients")
    sdspiSymNumClients.setMin(1)
    sdspiSymNumClients.setMax(10)
    sdspiSymNumClients.setDefaultValue(1)

    sdspiSymNumClients = sdspiComponent.createIntegerSymbol("DRV_SDSPI_SPEED_HZ", None)
    sdspiSymNumClients.setLabel("SD Card Speed (Hz)")
    sdspiSymNumClients.setMin(1)
    sdspiSymNumClients.setMax(25000000)
    sdspiSymNumClients.setDefaultValue(5000000)

    sdspiQueueSize = sdspiComponent.createIntegerSymbol("DRV_SDSPI_QUEUE_SIZE", None)
    sdspiQueueSize.setLabel("Transfer Queue Size")
    sdspiQueueSize.setMin(1)
    sdspiQueueSize.setMax(64)
    sdspiQueueSize.setVisible((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous"))
    sdspiQueueSize.setDefaultValue(4)
    sdspiQueueSize.setDependencies(asyncModeOptions, ["drv_sdspi.DRV_SDSPI_COMMON_MODE"])

    sdspiCardDetectionMethod = sdspiComponent.createComboSymbol("DRV_SDSPI_CARD_DETECTION_METHOD", None, cardDetectMethodComboValues)
    sdspiCardDetectionMethod.setLabel("Card Detection Method")
    sdspiCardDetectionMethod.setDefaultValue("Use Polling")
    sdspiCardDetectionMethod.setReadOnly(True)

    sdspiPollingInterval = sdspiComponent.createIntegerSymbol("DRV_SDSPI_POLLING_INTERVAL", None)
    sdspiPollingInterval.setLabel("Polling Interval (ms)")
    sdspiPollingInterval.setMin(1)
    sdspiPollingInterval.setDefaultValue(1000)

    sdspiFsEnable = sdspiComponent.createBooleanSymbol("DRV_SDSPI_FS_ENABLE", None)
    sdspiFsEnable.setLabel("File system for SDSPI Driver Enabled")
    sdspiFsEnable.setReadOnly(True)

    sdspiSymChipSelectPin = sdspiComponent.createKeyValueSetSymbol("DRV_SDSPI_CHIP_SELECT_PIN", None)
    sdspiSymChipSelectPin.setLabel("Chip Select Pin")
    sdspiSymChipSelectPin.setDefaultValue(0)
    sdspiSymChipSelectPin.setOutputMode("Key")
    sdspiSymChipSelectPin.setDisplayMode("Description")

    sdspiChipSelectPinComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_CHIP_SELECT_PIN_COMMENT", None)
    sdspiChipSelectPinComment.setLabel("!!! Configure the Chip Select pin as GPIO output under Pin Settings.!!! ")

    sdspiSymWriteProtect = sdspiComponent.createBooleanSymbol("DRV_SDSPI_ENABLE_WRITE_PROTECT_CHECKING", None)
    sdspiSymWriteProtect.setLabel("Use Write Protect Pin (Active High)?")

    sdspiSymWriteProtectPin = sdspiComponent.createKeyValueSetSymbol("DRV_SDSPI_WRITE_PROTECT_PIN", sdspiSymWriteProtect)
    sdspiSymWriteProtectPin.setLabel("Write Protect Pin (Active High)")
    sdspiSymWriteProtectPin.setDefaultValue(0)
    sdspiSymWriteProtectPin.setOutputMode("Key")
    sdspiSymWriteProtectPin.setDisplayMode("Description")
    sdspiSymWriteProtectPin.setVisible(sdspiSymWriteProtect.getValue())
    sdspiSymWriteProtectPin.setDependencies(showWriteProtectComment, ["DRV_SDSPI_ENABLE_WRITE_PROTECT_CHECKING"])

    sdspiWriteProtectPinComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_WRITE_PROTECT_PIN_COMMENT", sdspiSymWriteProtect)
    sdspiWriteProtectPinComment.setLabel("!!! Configure the Write Protect pin as GPIO input under Pin Settings. !!!")
    sdspiWriteProtectPinComment.setVisible(sdspiSymWriteProtect.getValue())
    sdspiWriteProtectPinComment.setDependencies(showWriteProtectComment, ["DRV_SDSPI_ENABLE_WRITE_PROTECT_CHECKING"])

    sdspiTXRXDMA = sdspiComponent.createBooleanSymbol("DRV_SDSPI_TX_RX_DMA", None)
    sdspiTXRXDMA.setLabel("Use DMA for Transmit and Receive ?")
    sdspiTXRXDMA.setVisible(isDMAPresent and sdspiInterfaceType.getValue() == "SPI_PLIB")
    sdspiTXRXDMA.setReadOnly(True)
    sdspiTXRXDMA.setDependencies(setPLIBOptionsVisibility, ["DRV_SDSPI_INTERFACE_TYPE"])

    sdspiTXRXDMAEn = sdspiComponent.createBooleanSymbol("DRV_SDSPI_TX_RX_DMA_EN", None)
    sdspiTXRXDMAEn.setVisible(False)
    sdspiTXRXDMAEn.setDefaultValue(False)
    sdspiTXRXDMAEn.setDependencies(updateDMAEnableCntr, ["DRV_SDSPI_TX_RX_DMA"])

    sdspiTXDMAChannel = sdspiComponent.createIntegerSymbol("DRV_SDSPI_TX_DMA_CHANNEL", None)
    sdspiTXDMAChannel.setLabel("DMA Channel For Transmit")
    sdspiTXDMAChannel.setDefaultValue(0)
    sdspiTXDMAChannel.setVisible(False)
    sdspiTXDMAChannel.setReadOnly(True)
    sdspiTXDMAChannel.setDependencies(requestAndAssignDMAChannel, ["DRV_SDSPI_TX_RX_DMA"])

    sdspiTXDMAChannelComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_TX_DMA_CH_COMMENT", None)
    sdspiTXDMAChannelComment.setLabel("Warning!!! Couldn't Allocate DMA Channel for Transmit. Check DMA manager. !!!")
    sdspiTXDMAChannelComment.setVisible(False)
    sdspiTXDMAChannelComment.setDependencies(requestDMAComment, ["DRV_SDSPI_TX_DMA_CHANNEL"])

    sdspiRXDMAChannel = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RX_DMA_CHANNEL", None)
    sdspiRXDMAChannel.setLabel("DMA Channel For Receive")
    sdspiRXDMAChannel.setDefaultValue(1)
    sdspiRXDMAChannel.setVisible(False)
    sdspiRXDMAChannel.setReadOnly(True)
    sdspiRXDMAChannel.setDependencies(requestAndAssignDMAChannel, ["DRV_SDSPI_TX_RX_DMA"])

    sdspiRXDMAChannelComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_RX_DMA_CH_COMMENT", None)
    sdspiRXDMAChannelComment.setLabel("Warning!!! Couldn't Allocate DMA Channel for Receive. Check DMA manager. !!!")
    sdspiRXDMAChannelComment.setVisible(False)
    sdspiRXDMAChannelComment.setDependencies(requestDMAComment, ["DRV_SDSPI_RX_DMA_CHANNEL"])

    sdspiDependencyDMAComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_DEPENDENCY_DMA_COMMENT", None)
    sdspiDependencyDMAComment.setLabel("!!! Satisfy PLIB Dependency to Allocate DMA Channel !!!")
    sdspiDependencyDMAComment.setVisible(False)

    # RTOS Settings
    sdspiRTOSMenu = sdspiComponent.createMenuSymbol("DRV_SDSPI_RTOS_MENU", None)
    sdspiRTOSMenu.setLabel("RTOS settings")
    sdspiRTOSMenu.setDescription("RTOS settings")
    sdspiRTOSMenu.setVisible((Database.getSymbolValue("HarmonyCore", "SELECT_RTOS") != "BareMetal"))
    sdspiRTOSMenu.setDependencies(showRTOSMenu, ["HarmonyCore.SELECT_RTOS"])

    sdspiRTOSTask = sdspiComponent.createComboSymbol("DRV_SDSPI_RTOS", sdspiRTOSMenu, ["Standalone"])
    sdspiRTOSTask.setLabel("Run Library Tasks As")
    sdspiRTOSTask.setDefaultValue("Standalone")
    sdspiRTOSTask.setVisible(False)

    sdspiRTOSStackSize = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RTOS_STACK_SIZE", sdspiRTOSMenu)
    sdspiRTOSStackSize.setLabel("Stack Size (in bytes)")
    sdspiRTOSStackSize.setDefaultValue(1024)

    sdspiRTOSMsgQSize = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RTOS_TASK_MSG_QTY", sdspiRTOSMenu)
    sdspiRTOSMsgQSize.setLabel("Maximum Message Queue Size")
    sdspiRTOSMsgQSize.setDescription("A µC/OS-III task contains an optional internal message queue (if OS_CFG_TASK_Q_EN is set to DEF_ENABLED in os_cfg.h). This argument specifies the maximum number of messages that the task can receive through this message queue. The user may specify that the task is unable to receive messages by setting this argument to 0")
    sdspiRTOSMsgQSize.setDefaultValue(0)
    sdspiRTOSMsgQSize.setVisible(getActiveRtos() == "MicriumOSIII")
    sdspiRTOSMsgQSize.setDependencies(sdspiRtosMicriumOSIIIAppTaskVisibility, ["HarmonyCore.SELECT_RTOS"])

    sdspiRTOSTaskTimeQuanta = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RTOS_TASK_TIME_QUANTA", sdspiRTOSMenu)
    sdspiRTOSTaskTimeQuanta.setLabel("Task Time Quanta")
    sdspiRTOSTaskTimeQuanta.setDescription("The amount of time (in clock ticks) for the time quanta when Round Robin is enabled. If you specify 0, then the default time quanta will be used which is the tick rate divided by 10.")
    sdspiRTOSTaskTimeQuanta.setDefaultValue(0)
    sdspiRTOSTaskTimeQuanta.setVisible(getActiveRtos() == "MicriumOSIII")
    sdspiRTOSTaskTimeQuanta.setDependencies(sdspiRtosMicriumOSIIIAppTaskVisibility, ["HarmonyCore.SELECT_RTOS"])

    sdspiRTOSTaskPriority = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RTOS_TASK_PRIORITY", sdspiRTOSMenu)
    sdspiRTOSTaskPriority.setLabel("Task Priority")
    sdspiRTOSTaskPriority.setDefaultValue(1)

    sdspiRTOSTaskDelay = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_USE_DELAY", sdspiRTOSMenu)
    sdspiRTOSTaskDelay.setLabel("Use Task Delay?")
    sdspiRTOSTaskDelay.setDefaultValue(True)
    sdspiRTOSTaskDelay.setVisible(True)
    sdspiRTOSTaskDelay.setReadOnly(True)

    sdspiRTOSTaskDelayVal = sdspiComponent.createIntegerSymbol("DRV_SDSPI_RTOS_DELAY", sdspiRTOSMenu)
    sdspiRTOSTaskDelayVal.setLabel("Task Delay (ms)")
    sdspiRTOSTaskDelayVal.setMin(1)
    sdspiRTOSTaskDelayVal.setMax(10000)
    sdspiRTOSTaskDelayVal.setDefaultValue(10)
    sdspiRTOSTaskDelayVal.setVisible((sdspiRTOSTaskDelay.getValue() == True))
    sdspiRTOSTaskDelayVal.setDependencies(setVisible, ["DRV_SDSPI_RTOS_USE_DELAY"])

    sdspiRTOSTaskSpecificOpt = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_TASK_OPT_NONE", sdspiRTOSMenu)
    sdspiRTOSTaskSpecificOpt.setLabel("Task Specific Options")
    sdspiRTOSTaskSpecificOpt.setDescription("Contains task-specific options. Each option consists of one bit. The option is selected when the bit is set. The current version of µC/OS-III supports the following options:")
    sdspiRTOSTaskSpecificOpt.setDefaultValue(True)
    sdspiRTOSTaskSpecificOpt.setVisible(getActiveRtos() == "MicriumOSIII")
    sdspiRTOSTaskSpecificOpt.setDependencies(sdspiRtosMicriumOSIIIAppTaskVisibility, ["HarmonyCore.SELECT_RTOS"])

    sdspiRTOSTaskStkChk = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_TASK_OPT_STK_CHK", sdspiRTOSTaskSpecificOpt)
    sdspiRTOSTaskStkChk.setLabel("Stack checking is allowed for the task")
    sdspiRTOSTaskStkChk.setDescription("Specifies whether stack checking is allowed for the task")
    sdspiRTOSTaskStkChk.setDefaultValue(True)
    sdspiRTOSTaskStkChk.setDependencies(sdspiRtosMicriumOSIIITaskOptVisibility, ["DRV_SDSPI_RTOS_TASK_OPT_NONE"])

    sdspiRTOSTaskStkClr = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_TASK_OPT_STK_CLR", sdspiRTOSTaskSpecificOpt)
    sdspiRTOSTaskStkClr.setLabel("Stack needs to be cleared")
    sdspiRTOSTaskStkClr.setDescription("Specifies whether the stack needs to be cleared")
    sdspiRTOSTaskStkClr.setDefaultValue(True)
    sdspiRTOSTaskStkClr.setDependencies(sdspiRtosMicriumOSIIITaskOptVisibility, ["DRV_SDSPI_RTOS_TASK_OPT_NONE"])

    sdspiRTOSTaskSaveFp = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_TASK_OPT_SAVE_FP", sdspiRTOSTaskSpecificOpt)
    sdspiRTOSTaskSaveFp.setLabel("Floating-point registers needs to be saved")
    sdspiRTOSTaskSaveFp.setDescription("Specifies whether floating-point registers are saved. This option is only valid if the processor has floating-point hardware and the processor-specific code saves the floating-point registers")
    sdspiRTOSTaskSaveFp.setDefaultValue(False)
    sdspiRTOSTaskSaveFp.setDependencies(sdspiRtosMicriumOSIIITaskOptVisibility, ["DRV_SDSPI_RTOS_TASK_OPT_NONE"])

    sdspiRTOSTaskNoTls = sdspiComponent.createBooleanSymbol("DRV_SDSPI_RTOS_TASK_OPT_NO_TLS", sdspiRTOSTaskSpecificOpt)
    sdspiRTOSTaskNoTls.setLabel("TLS (Thread Local Storage) support needed for the task")
    sdspiRTOSTaskNoTls.setDescription("If the caller doesn’t want or need TLS (Thread Local Storage) support for the task being created. If you do not include this option, TLS will be supported by default. TLS support was added in V3.03.00")
    sdspiRTOSTaskNoTls.setDefaultValue(False)
    sdspiRTOSTaskNoTls.setDependencies(sdspiRtosMicriumOSIIITaskOptVisibility, ["DRV_SDSPI_RTOS_TASK_OPT_NONE"])

    sdspiDependencyComment = sdspiComponent.createCommentSymbol("DRV_SDSPI_DEPENDENCY_COMMENT", None)
    sdspiDependencyComment.setLabel("!!! Note: For each instance of SDSPI, connect either SPI PLIB or SPI Driver !!! ")

    availablePinDictionary = {}

    # Send message to core to get available pins
    availablePinDictionary = Database.sendMessage("core", "PIN_LIST", availablePinDictionary)

    for pad in sort_alphanumeric(availablePinDictionary.values()):
        key = "SYS_PORT_PIN_" + pad
        value = list(availablePinDictionary.keys())[list(availablePinDictionary.values()).index(pad)]
        description = pad
        sdspiSymChipSelectPin.addKey(key, value, description)
        sdspiSymWriteProtectPin.addKey(key, value, description)

    ############################################################################
    #### Code Generation ####
    ############################################################################

    configName = Variables.get("__CONFIGURATION_NAME")

    # System Template Files
    sdspiSymSystemDefObjFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYSTEM_DEF_OBJECT", None)
    sdspiSymSystemDefObjFile.setType("STRING")
    sdspiSymSystemDefObjFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_OBJECTS")
    sdspiSymSystemDefObjFile.setSourcePath("driver/sdspi/templates/system/system_definitions_objects.h.ftl")
    sdspiSymSystemDefObjFile.setMarkup(True)

    sdspiSymSystemConfigFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYSTEM_CONFIG", None)
    sdspiSymSystemConfigFile.setType("STRING")
    sdspiSymSystemConfigFile.setOutputName("core.LIST_SYSTEM_CONFIG_H_DRIVER_CONFIGURATION")
    sdspiSymSystemConfigFile.setSourcePath("driver/sdspi/templates/system/system_config.h.ftl")
    sdspiSymSystemConfigFile.setMarkup(True)

    sdspiSymSystemInitDataFile = sdspiComponent.createFileSymbol("DRV_SDSPI_INIT_DATA", None)
    sdspiSymSystemInitDataFile.setType("STRING")
    sdspiSymSystemInitDataFile.setOutputName("core.LIST_SYSTEM_INIT_C_DRIVER_INITIALIZATION_DATA")
    sdspiSymSystemInitDataFile.setSourcePath("driver/sdspi/templates/system/system_initialize_data.c.ftl")
    sdspiSymSystemInitDataFile.setMarkup(True)

    sdspiSymSystemInitFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYS_INIT", None)
    sdspiSymSystemInitFile.setType("STRING")
    sdspiSymSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_DRIVERS")
    sdspiSymSystemInitFile.setSourcePath("driver/sdspi/templates/system/system_initialize.c.ftl")
    sdspiSymSystemInitFile.setMarkup(True)

    sdspiSystemTasksFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYS_TASK", None)
    sdspiSystemTasksFile.setType("STRING")
    sdspiSystemTasksFile.setOutputName("core.LIST_SYSTEM_TASKS_C_CALL_DRIVER_TASKS")
    sdspiSystemTasksFile.setSourcePath("driver/sdspi/templates/system/system_tasks.c.ftl")
    sdspiSystemTasksFile.setMarkup(True)

    sdspiSystemRtosTasksFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYS_RTOS_TASK", None)
    sdspiSystemRtosTasksFile.setType("STRING")
    sdspiSystemRtosTasksFile.setOutputName("core.LIST_SYSTEM_RTOS_TASKS_C_DEFINITIONS")
    sdspiSystemRtosTasksFile.setSourcePath("driver/sdspi/templates/system/system_rtos_tasks.c.ftl")
    sdspiSystemRtosTasksFile.setMarkup(True)
    sdspiSystemRtosTasksFile.setEnabled((Database.getSymbolValue("Harmony", "SELECT_RTOS") != "BareMetal"))
    sdspiSystemRtosTasksFile.setDependencies(genRtosTask, ["Harmony.SELECT_RTOS"])

    # Global Header Files

    sdspiSymHeaderDefFile = sdspiComponent.createFileSymbol("DRV_SDSPI_DEF", None)
    sdspiSymHeaderDefFile.setSourcePath("driver/sdspi/templates/drv_sdspi_definitions.h.ftl")
    sdspiSymHeaderDefFile.setOutputName("drv_sdspi_definitions.h")
    sdspiSymHeaderDefFile.setDestPath("driver/sdspi")
    sdspiSymHeaderDefFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSymHeaderDefFile.setType("HEADER")
    sdspiSymHeaderDefFile.setMarkup(True)
    sdspiSymHeaderDefFile.setOverwrite(True)

    # Async Source Files
    sdspiAsyncSymSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_SOURCE", None)
    sdspiAsyncSymSourceFile.setSourcePath("driver/sdspi/async/src/drv_sdspi.c.ftl")
    sdspiAsyncSymSourceFile.setOutputName("drv_sdspi.c")
    sdspiAsyncSymSourceFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymSourceFile.setType("SOURCE")
    sdspiAsyncSymSourceFile.setOverwrite(True)
    sdspiAsyncSymSourceFile.setMarkup(True)
    sdspiAsyncSymSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous"))
    sdspiAsyncSymSourceFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE"])

    sdspiAsyncSymHeaderLocalFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_HEADER_LOCAL", None)
    sdspiAsyncSymHeaderLocalFile.setSourcePath("driver/sdspi/async/src/drv_sdspi_local.h.ftl")
    sdspiAsyncSymHeaderLocalFile.setOutputName("drv_sdspi_local.h")
    sdspiAsyncSymHeaderLocalFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymHeaderLocalFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymHeaderLocalFile.setType("HEADER")
    sdspiAsyncSymHeaderLocalFile.setOverwrite(True)
    sdspiAsyncSymHeaderLocalFile.setMarkup(True)
    sdspiAsyncSymHeaderLocalFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous"))
    sdspiAsyncSymHeaderLocalFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE"])

    sdspiAsyncSymPlibInterfaceSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_PLIB_INTERFACE_SOURCE", None)
    sdspiAsyncSymPlibInterfaceSourceFile.setSourcePath("driver/sdspi/async/src/drv_sdspi_plib_interface.c.ftl")
    sdspiAsyncSymPlibInterfaceSourceFile.setOutputName("drv_sdspi_plib_interface.c")
    sdspiAsyncSymPlibInterfaceSourceFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymPlibInterfaceSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymPlibInterfaceSourceFile.setType("SOURCE")
    sdspiAsyncSymPlibInterfaceSourceFile.setOverwrite(True)
    sdspiAsyncSymPlibInterfaceSourceFile.setMarkup(True)
    sdspiAsyncSymPlibInterfaceSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous") and (sdspiInterfaceType.getValue() == "SPI_PLIB"))
    sdspiAsyncSymPlibInterfaceSourceFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiAsyncSymDriverInterfaceSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_DRIVER_INTERFACE_SOURCE", None)
    sdspiAsyncSymDriverInterfaceSourceFile.setSourcePath("driver/sdspi/async/src/drv_sdspi_driver_interface.c.ftl")
    sdspiAsyncSymDriverInterfaceSourceFile.setOutputName("drv_sdspi_driver_interface.c")
    sdspiAsyncSymDriverInterfaceSourceFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymDriverInterfaceSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymDriverInterfaceSourceFile.setType("SOURCE")
    sdspiAsyncSymDriverInterfaceSourceFile.setOverwrite(True)
    sdspiAsyncSymDriverInterfaceSourceFile.setMarkup(True)
    sdspiAsyncSymDriverInterfaceSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous") and (sdspiInterfaceType.getValue() == "SPI_DRV"))
    sdspiAsyncSymDriverInterfaceSourceFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiAsyncSymPlibInterfaceHeaderFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_PLIB_INTERFACE_HEADER", None)
    sdspiAsyncSymPlibInterfaceHeaderFile.setSourcePath("driver/sdspi/async/src/drv_sdspi_plib_interface.h.ftl")
    sdspiAsyncSymPlibInterfaceHeaderFile.setOutputName("drv_sdspi_plib_interface.h")
    sdspiAsyncSymPlibInterfaceHeaderFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymPlibInterfaceHeaderFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymPlibInterfaceHeaderFile.setType("HEADER")
    sdspiAsyncSymPlibInterfaceHeaderFile.setOverwrite(True)
    sdspiAsyncSymPlibInterfaceHeaderFile.setMarkup(True)
    sdspiAsyncSymPlibInterfaceHeaderFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous") and (sdspiInterfaceType.getValue() == "SPI_PLIB"))
    sdspiAsyncSymPlibInterfaceHeaderFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiAsyncSymDriverInterfaceHeaderFile = sdspiComponent.createFileSymbol("DRV_SDSPI_ASYNC_DRIVER_INTERFACE_HEADER", None)
    sdspiAsyncSymDriverInterfaceHeaderFile.setSourcePath("driver/sdspi/async/src/drv_sdspi_driver_interface.h.ftl")
    sdspiAsyncSymDriverInterfaceHeaderFile.setOutputName("drv_sdspi_driver_interface.h")
    sdspiAsyncSymDriverInterfaceHeaderFile.setDestPath("driver/sdspi/src")
    sdspiAsyncSymDriverInterfaceHeaderFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiAsyncSymDriverInterfaceHeaderFile.setType("HEADER")
    sdspiAsyncSymDriverInterfaceHeaderFile.setOverwrite(True)
    sdspiAsyncSymDriverInterfaceHeaderFile.setMarkup(True)
    sdspiAsyncSymDriverInterfaceHeaderFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Asynchronous") and (sdspiInterfaceType.getValue() == "SPI_DRV"))
    sdspiAsyncSymDriverInterfaceHeaderFile.setDependencies(asyncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    # Sync file generation

    sdspiSyncSymSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_SOURCE", None)
    sdspiSyncSymSourceFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi.c.ftl")
    sdspiSyncSymSourceFile.setOutputName("drv_sdspi.c")
    sdspiSyncSymSourceFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymSourceFile.setType("SOURCE")
    sdspiSyncSymSourceFile.setOverwrite(True)
    sdspiSyncSymSourceFile.setMarkup(True)
    sdspiSyncSymSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous"))
    sdspiSyncSymSourceFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE"])

    sdspiSyncSymHeaderLocalFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_HEADER_LOCAL", None)
    sdspiSyncSymHeaderLocalFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi_local.h.ftl")
    sdspiSyncSymHeaderLocalFile.setOutputName("drv_sdspi_local.h")
    sdspiSyncSymHeaderLocalFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymHeaderLocalFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymHeaderLocalFile.setType("HEADER")
    sdspiSyncSymHeaderLocalFile.setOverwrite(True)
    sdspiSyncSymHeaderLocalFile.setMarkup(True)
    sdspiSyncSymHeaderLocalFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous"))
    sdspiSyncSymHeaderLocalFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE"])

    sdspiSyncSymPlibInterfaceSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_PLIB_INTERFACE_SOURCE", None)
    sdspiSyncSymPlibInterfaceSourceFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi_plib_interface.c.ftl")
    sdspiSyncSymPlibInterfaceSourceFile.setOutputName("drv_sdspi_plib_interface.c")
    sdspiSyncSymPlibInterfaceSourceFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymPlibInterfaceSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymPlibInterfaceSourceFile.setType("SOURCE")
    sdspiSyncSymPlibInterfaceSourceFile.setOverwrite(True)
    sdspiSyncSymPlibInterfaceSourceFile.setMarkup(True)
    sdspiSyncSymPlibInterfaceSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous") and (sdspiInterfaceType.getValue() == "SPI_PLIB"))
    sdspiSyncSymPlibInterfaceSourceFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiSyncSymDriverInterfaceSourceFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_DRIVER_INTERFACE_SOURCE", None)
    sdspiSyncSymDriverInterfaceSourceFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi_driver_interface.c.ftl")
    sdspiSyncSymDriverInterfaceSourceFile.setOutputName("drv_sdspi_driver_interface.c")
    sdspiSyncSymDriverInterfaceSourceFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymDriverInterfaceSourceFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymDriverInterfaceSourceFile.setType("SOURCE")
    sdspiSyncSymDriverInterfaceSourceFile.setOverwrite(True)
    sdspiSyncSymDriverInterfaceSourceFile.setMarkup(True)
    sdspiSyncSymDriverInterfaceSourceFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous") and (sdspiInterfaceType.getValue() == "SPI_DRV"))
    sdspiSyncSymDriverInterfaceSourceFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiSyncSymPlibInterfaceHeaderFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_PLIB_INTERFACE_HEADER", None)
    sdspiSyncSymPlibInterfaceHeaderFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi_plib_interface.h.ftl")
    sdspiSyncSymPlibInterfaceHeaderFile.setOutputName("drv_sdspi_plib_interface.h")
    sdspiSyncSymPlibInterfaceHeaderFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymPlibInterfaceHeaderFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymPlibInterfaceHeaderFile.setType("HEADER")
    sdspiSyncSymPlibInterfaceHeaderFile.setOverwrite(True)
    sdspiSyncSymPlibInterfaceHeaderFile.setMarkup(True)
    sdspiSyncSymPlibInterfaceHeaderFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous") and (sdspiInterfaceType.getValue() == "SPI_PLIB"))
    sdspiSyncSymPlibInterfaceHeaderFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

    sdspiSyncSymDriverInterfaceHeaderFile = sdspiComponent.createFileSymbol("DRV_SDSPI_SYNC_DRIVER_INTERFACE_HEADER", None)
    sdspiSyncSymDriverInterfaceHeaderFile.setSourcePath("driver/sdspi/sync/src/drv_sdspi_driver_interface.h.ftl")
    sdspiSyncSymDriverInterfaceHeaderFile.setOutputName("drv_sdspi_driver_interface.h")
    sdspiSyncSymDriverInterfaceHeaderFile.setDestPath("driver/sdspi/src")
    sdspiSyncSymDriverInterfaceHeaderFile.setProjectPath("config/" + configName + "/driver/sdspi/")
    sdspiSyncSymDriverInterfaceHeaderFile.setType("HEADER")
    sdspiSyncSymDriverInterfaceHeaderFile.setOverwrite(True)
    sdspiSyncSymDriverInterfaceHeaderFile.setMarkup(True)
    sdspiSyncSymDriverInterfaceHeaderFile.setEnabled((Database.getSymbolValue("drv_sdspi", "DRV_SDSPI_COMMON_MODE") == "Synchronous") and (sdspiInterfaceType.getValue() == "SPI_DRV"))
    sdspiSyncSymDriverInterfaceHeaderFile.setDependencies(syncFileGenration, ["drv_sdspi.DRV_SDSPI_COMMON_MODE", "DRV_SDSPI_INTERFACE_TYPE"])

def onAttachmentConnected(source, target):
    global sdcardFsEnable
    global isDMAPresent

    localComponent = source["component"]
    remoteComponent = target["component"]
    remoteID = remoteComponent.getID()
    connectID = source["id"]
    targetID = target["id"]

    # For Capability Connected (drv_sdcard)
    if (connectID == "drv_media"):
        if (remoteID == "sys_fs"):
            sdspiFsEnable.setValue(True)
            sdspiFsConnectionCounterDict = {}
            sdspiFsConnectionCounterDict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_FS_CONNECTION_COUNTER_INC", sdspiFsConnectionCounterDict)

    # For Dependency Connected SPI PLIB
    if (connectID == "drv_sdspi_SPI_dependency"):
        plibUsed = localComponent.getSymbolByID("DRV_SDSPI_PLIB")
        plibUsed.clearValue()
        plibUsed.setValue(remoteID.upper())

        localComponent.setSymbolValue("DRV_SDSPI_INTERFACE_TYPE", "SPI_PLIB")

        # Do not change the order as DMA Channels needs to be allocated
        # after setting the plibUsed symbol
        if isDMAPresent == True:
            localComponent.getSymbolByID("DRV_SDSPI_TX_RX_DMA").setReadOnly(False)
            # Enable "Enable System DMA" option in MHC
            if (Database.getSymbolValue("HarmonyCore", "ENABLE_SYS_DMA") == False):
                Database.setSymbolValue("HarmonyCore", "ENABLE_SYS_DMA", True)
            #localComponent.getSymbolByID("DRV_SDSPI_DEPENDENCY_DMA_COMMENT").setVisible(False)

    elif (connectID == "drv_sdspi_DRV_SPI_dependency"):
        localComponent.setSymbolValue("DRV_SDSPI_INTERFACE_TYPE", "SPI_DRV")
        drvInstance = localComponent.getSymbolByID("DRV_SDSPI_SPI_DRIVER_INSTANCE")
        drvInstance.clearValue()
        index = Database.getSymbolValue(remoteID, "INDEX")
        drvInstance.setValue(str(index))
        result_dict = {}
        result_dict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_SPI_DRIVER_CONNECTION_COUNTER_INC", result_dict)

def onAttachmentDisconnected(source, target):
    global sdcardFsEnable
    global isDMAPresent

    localComponent = source["component"]
    remoteComponent = target["component"]
    remoteID = remoteComponent.getID()
    connectID = source["id"]
    targetID = target["id"]

    # For Capability Disconnected (drv_sdcard)
    if (connectID == "drv_media"):
        if (remoteID == "sys_fs"):
            sdspiFsEnable.setValue(False)
            sdspiFsConnectionCounterDict = {}
            sdspiFsConnectionCounterDict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_FS_CONNECTION_COUNTER_DEC", sdspiFsConnectionCounterDict)

    # For Dependency Disonnected (SPI)
    if (connectID == "drv_sdspi_SPI_dependency"):

        dummyDict = {}
        dummyDict = Database.sendMessage(remoteID, "SPI_MASTER_MODE", {"isReadOnly":False})
        dummyDict = Database.sendMessage(remoteID, "SPI_MASTER_INTERRUPT_MODE", {"isReadOnly":False})
        dummyDict = Database.sendMessage(remoteID, "SPI_MASTER_HARDWARE_CS", {"isReadOnly":False})

        # Do not change the order as DMA Channels needs to be cleared
        # before clearing the plibUsed symbol
        if isDMAPresent == True:
            localComponent.getSymbolByID("DRV_SDSPI_TX_RX_DMA").clearValue()
            localComponent.getSymbolByID("DRV_SDSPI_TX_RX_DMA").setReadOnly(True)
            #localComponent.getSymbolByID("DRV_SDSPI_DEPENDENCY_DMA_COMMENT").setVisible(True)

        plibUsed = localComponent.getSymbolByID("DRV_SDSPI_PLIB")
        plibUsed.clearValue()
        localComponent.setSymbolValue("DRV_SDSPI_INTERFACE_TYPE", "")
    elif (connectID == "drv_sdspi_DRV_SPI_dependency"):

        drvInstance = localComponent.getSymbolByID("DRV_SDSPI_SPI_DRIVER_INSTANCE")
        drvInstance.clearValue()
        result_dict = {}
        result_dict = Database.sendMessage("drv_sdspi", "DRV_SDSPI_SPI_DRIVER_CONNECTION_COUNTER_DEC", result_dict)
        localComponent.setSymbolValue("DRV_SDSPI_INTERFACE_TYPE", "")
