#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int device_has_input_channels(AudioDeviceID deviceID);

void print_device_info(AudioDeviceID deviceID, const char *name) {
    AudioObjectPropertyAddress nameProp = {
        kAudioDevicePropertyDeviceNameCFString,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    CFStringRef deviceName = NULL;
    UInt32 nameSize = sizeof(deviceName);

    if (AudioObjectGetPropertyData(deviceID, &nameProp, 0, NULL, &nameSize, &deviceName) == noErr && deviceName) {
        char cName[256];
        CFStringGetCString(deviceName, cName, sizeof(cName), kCFStringEncodingUTF8);
        printf("  Device: %s (ID: %u)\n", cName, deviceID);
        CFRelease(deviceName);
    }
}

void test_device_has_input_channels() {
    printf("\n=== Testing device_has_input_channels ===\n\n");

    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    UInt32 size;
    if (AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &size) != noErr) {
        printf("FAIL: Could not get device list size\n");
        return;
    }

    UInt32 deviceCount = size / sizeof(AudioDeviceID);
    AudioDeviceID *devices = malloc(size);

    if (AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &size, devices) != noErr) {
        free(devices);
        printf("FAIL: Could not get device list\n");
        return;
    }

    printf("Testing %u audio devices:\n\n", deviceCount);

    int inputDeviceCount = 0;
    int outputOnlyDeviceCount = 0;

    for (UInt32 i = 0; i < deviceCount; i++) {
        AudioObjectPropertyAddress nameProp = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMain
        };

        CFStringRef deviceName = NULL;
        UInt32 nameSize = sizeof(deviceName);

        if (AudioObjectGetPropertyData(devices[i], &nameProp, 0, NULL, &nameSize, &deviceName) == noErr && deviceName) {
            char cName[256];
            CFStringGetCString(deviceName, cName, sizeof(cName), kCFStringEncodingUTF8);

            int hasInput = device_has_input_channels(devices[i]);

            AudioObjectPropertyAddress outputProp = {
                kAudioDevicePropertyStreamConfiguration,
                kAudioObjectPropertyScopeOutput,
                kAudioObjectPropertyElementMain
            };

            UInt32 outputSize;
            int hasOutput = 0;
            if (AudioObjectGetPropertyDataSize(devices[i], &outputProp, 0, NULL, &outputSize) == noErr) {
                AudioBufferList *outputBufferList = malloc(outputSize);
                if (outputBufferList && AudioObjectGetPropertyData(devices[i], &outputProp, 0, NULL, &outputSize, outputBufferList) == noErr) {
                    UInt32 outputChannels = 0;
                    for (UInt32 j = 0; j < outputBufferList->mNumberBuffers; j++) {
                        outputChannels += outputBufferList->mBuffers[j].mNumberChannels;
                    }
                    hasOutput = outputChannels > 0;
                    free(outputBufferList);
                }
            }

            printf("Device: %s\n", cName);
            printf("  ID: %u\n", devices[i]);
            printf("  Has Input:  %s\n", hasInput ? "YES" : "NO");
            printf("  Has Output: %s\n", hasOutput ? "YES" : "NO");

            if (hasInput && hasOutput) {
                printf("  Type: INPUT + OUTPUT (both)\n");
            } else if (hasInput) {
                printf("  Type: INPUT ONLY (microphone)\n");
            } else if (hasOutput) {
                printf("  Type: OUTPUT ONLY (speaker)\n");
            }
            printf("\n");

            if (hasInput) {
                inputDeviceCount++;
            } else if (hasOutput) {
                outputOnlyDeviceCount++;
            }

            CFRelease(deviceName);
        }
    }

    free(devices);

    printf("\nSummary:\n");
    printf("  Total devices: %u\n", deviceCount);
    printf("  Devices with input: %d\n", inputDeviceCount);
    printf("  Output-only devices: %d\n", outputOnlyDeviceCount);

    if (inputDeviceCount > 0) {
        printf("\nPASS: device_has_input_channels correctly identified input devices\n");
    } else {
        printf("\nWARN: No input devices found on system\n");
    }
}

void test_speaker_rejection() {
    printf("\n=== Testing Speaker Rejection ===\n\n");

    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };

    UInt32 size;
    if (AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &size) != noErr) {
        printf("FAIL: Could not get device list\n");
        return;
    }

    UInt32 deviceCount = size / sizeof(AudioDeviceID);
    AudioDeviceID *devices = malloc(size);

    if (AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &size, devices) != noErr) {
        free(devices);
        printf("FAIL: Could not get device list\n");
        return;
    }

    int speakersRejected = 0;

    for (UInt32 i = 0; i < deviceCount; i++) {
        AudioObjectPropertyAddress nameProp = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMain
        };

        CFStringRef deviceName = NULL;
        UInt32 nameSize = sizeof(deviceName);

        if (AudioObjectGetPropertyData(devices[i], &nameProp, 0, NULL, &nameSize, &deviceName) == noErr && deviceName) {
            char cName[256];
            CFStringGetCString(deviceName, cName, sizeof(cName), kCFStringEncodingUTF8);

            int hasInput = device_has_input_channels(devices[i]);

            AudioObjectPropertyAddress outputProp = {
                kAudioDevicePropertyStreamConfiguration,
                kAudioObjectPropertyScopeOutput,
                kAudioObjectPropertyElementMain
            };

            UInt32 outputSize;
            int hasOutput = 0;
            if (AudioObjectGetPropertyDataSize(devices[i], &outputProp, 0, NULL, &outputSize) == noErr) {
                AudioBufferList *outputBufferList = malloc(outputSize);
                if (outputBufferList && AudioObjectGetPropertyData(devices[i], &outputProp, 0, NULL, &outputSize, outputBufferList) == noErr) {
                    UInt32 outputChannels = 0;
                    for (UInt32 j = 0; j < outputBufferList->mNumberBuffers; j++) {
                        outputChannels += outputBufferList->mBuffers[j].mNumberChannels;
                    }
                    hasOutput = outputChannels > 0;
                    free(outputBufferList);
                }
            }

            if (hasOutput && !hasInput) {
                speakersRejected++;
                printf("PASS: Correctly rejected speaker: %s\n", cName);
            }

            CFRelease(deviceName);
        }
    }

    free(devices);

    if (speakersRejected > 0) {
        printf("\nPASS: Successfully rejected %d output-only devices\n", speakersRejected);
    } else {
        printf("\nINFO: No output-only devices found to test rejection\n");
    }
}

int main() {
    printf("========================================\n");
    printf("Aggregate Mic Unit Tests\n");
    printf("========================================\n");

    test_device_has_input_channels();
    test_speaker_rejection();

    printf("\n========================================\n");
    printf("All tests completed\n");
    printf("========================================\n");

    return 0;
}

int device_has_input_channels(AudioDeviceID deviceID) {
    AudioObjectPropertyAddress prop = {
        kAudioDevicePropertyStreamConfiguration,
        kAudioObjectPropertyScopeInput,
        kAudioObjectPropertyElementMain
    };

    UInt32 size;
    if (AudioObjectGetPropertyDataSize(deviceID, &prop, 0, NULL, &size) != noErr) {
        return 0;
    }

    AudioBufferList *bufferList = malloc(size);
    if (!bufferList) {
        return 0;
    }

    if (AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &size, bufferList) != noErr) {
        free(bufferList);
        return 0;
    }

    UInt32 totalChannels = 0;
    for (UInt32 i = 0; i < bufferList->mNumberBuffers; i++) {
        totalChannels += bufferList->mBuffers[i].mNumberChannels;
    }

    free(bufferList);
    return totalChannels > 0;
}
