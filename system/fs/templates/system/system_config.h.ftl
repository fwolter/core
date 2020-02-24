<#--
/*******************************************************************************
  File System Service Freemarker Template File

  Company:
    Microchip Technology Inc.

  File Name:
    sys_devcon.h

  Summary:
   File System Service Freemarker Template File

  Description:

*******************************************************************************/

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
-->

/* File System Service Configuration */

#define SYS_FS_MEDIA_NUMBER               ${SYS_FS_INSTANCES_NUMBER}

<#if SYS_FS_AUTO_MOUNT != true>
    <#lt>#define SYS_FS_VOLUME_NUMBER              ${SYS_FS_VOLUME_NUMBER}
<#elseif SYS_FS_IDX0 == true && SYS_FS_IDX1 == true && SYS_FS_IDX2 == true && SYS_FS_IDX3 == true>
    <#lt>#define SYS_FS_VOLUME_NUMBER            (${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX0} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX1} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX2} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX3})
<#elseif SYS_FS_IDX0 == true && SYS_FS_IDX1 == true && SYS_FS_IDX2 == true>
    <#lt>#define SYS_FS_VOLUME_NUMBER             (${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX0} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX1} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX2})
<#elseif SYS_FS_IDX0 == true && SYS_FS_IDX1 == true>
    <#lt>#define SYS_FS_VOLUME_NUMBER              (${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX0} + ${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX1})
<#elseif SYS_FS_IDX0 == true>
    <#lt>#define SYS_FS_VOLUME_NUMBER              (${SYS_FS_VOLUME_INSTANCES_NUMBER_IDX0})
</#if>

<#if SYS_FS_AUTO_MOUNT == true>
    <#lt>#define SYS_FS_AUTOMOUNT_ENABLE           true
    <#lt>#define SYS_FS_CLIENT_NUMBER              ${SYS_FS_CLIENT_NUMBER}
<#else>
    <#lt>#define SYS_FS_AUTOMOUNT_ENABLE           false
</#if>
#define SYS_FS_MAX_FILES                  ${SYS_FS_MAX_FILES}
#define SYS_FS_MAX_FILE_SYSTEM_TYPE       ${SYS_FS_MAX_FILE_SYSTEM_TYPE}
#define SYS_FS_MEDIA_MAX_BLOCK_SIZE       ${SYS_FS_MEDIA_MAX_BLOCK_SIZE}
#define SYS_FS_MEDIA_MANAGER_BUFFER_SIZE  ${SYS_FS_MEDIA_MANAGER_BUFFER_SIZE}
#define SYS_FS_USE_LFN                    1
#define SYS_FS_FILE_NAME_LEN              ${SYS_FS_FILE_NAME_LEN}
#define SYS_FS_CWD_STRING_LEN             ${SYS_FS_CWD_STRING_LEN}

<#if SYS_FS_FAT == true>
    <#lt>#define FAT_FS_USE_LFN                    SYS_FS_USE_LFN
    <#lt>#define FAT_FS_MAX_LFN                    SYS_FS_FILE_NAME_LEN
    <#lt>#define FAT_FS_MAX_SS                     SYS_FS_MEDIA_MAX_BLOCK_SIZE
</#if>

<#if (HarmonyCore.SELECT_RTOS)?? && HarmonyCore.SELECT_RTOS != "BareMetal">
    <#lt>/* File System RTOS Configurations*/
    <#if (HarmonyCore.SELECT_RTOS)?? && HarmonyCore.SELECT_RTOS == "FreeRTOS">
        <#lt>#define SYS_FS_STACK_SIZE                 ${SYS_FS_RTOS_STACK_SIZE / 4}
    <#else>
        <#lt>#define SYS_FS_STACK_SIZE                 ${SYS_FS_RTOS_STACK_SIZE}
    </#if>
    <#lt>#define SYS_FS_PRIORITY                   ${SYS_FS_RTOS_TASK_PRIORITY}
    <#if (HarmonyCore.SELECT_RTOS)?? && HarmonyCore.SELECT_RTOS == "MicriumOSIII">
        <#lt>#define SYS_FS_RTOS_TASK_MSG_QTY          ${SYS_FS_RTOS_TASK_MSG_QTY}u
        <#lt>#define SYS_FS_RTOS_TASK_TIME_QUANTA      ${SYS_FS_RTOS_TASK_TIME_QUANTA}u
    </#if>
</#if>

<#--
/*******************************************************************************
 End of File
*/
-->

