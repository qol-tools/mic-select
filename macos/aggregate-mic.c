#include <CoreAudio/CoreAudio.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

AudioDeviceID find_device_by_name(const char *name) {
    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    
    UInt32 size;
    if (AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop, 0, NULL, &size) != noErr) {
        return kAudioDeviceUnknown;
    }
    
    UInt32 deviceCount = size / sizeof(AudioDeviceID);
    AudioDeviceID *devices = malloc(size);
    
    if (AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, &size, devices) != noErr) {
        free(devices);
        return kAudioDeviceUnknown;
    }
    
    AudioDeviceID found = kAudioDeviceUnknown;
    for (UInt32 i = 0; i < deviceCount; i++) {
        CFStringRef deviceName = NULL;
        UInt32 nameSize = sizeof(deviceName);
        AudioObjectPropertyAddress nameProp = {
            kAudioDevicePropertyDeviceNameCFString,
            kAudioObjectPropertyScopeGlobal,
            kAudioObjectPropertyElementMain
        };
        
        if (AudioObjectGetPropertyData(devices[i], &nameProp, 0, NULL, &nameSize, &deviceName) == noErr && deviceName) {
            char cName[256];
            CFStringGetCString(deviceName, cName, sizeof(cName), kCFStringEncodingUTF8);
            CFRelease(deviceName);
            
            if (strstr(cName, name) != NULL) {
                found = devices[i];
                break;
            }
        }
    }
    
    free(devices);
    return found;
}

CFStringRef get_device_uid(AudioDeviceID deviceID) {
    CFStringRef uid = NULL;
    UInt32 size = sizeof(uid);
    AudioObjectPropertyAddress prop = {
        kAudioDevicePropertyDeviceUID,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    
    if (AudioObjectGetPropertyData(deviceID, &prop, 0, NULL, &size, &uid) == noErr) {
        return uid;
    }
    return NULL;
}

int set_aggregate_to_single_device(AudioDeviceID aggID, CFStringRef targetUID) {
    AudioObjectPropertyAddress prop = {
        kAudioAggregateDevicePropertyFullSubDeviceList,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    
    CFArrayRef currentList = NULL;
    UInt32 size = sizeof(currentList);
    
    OSStatus err = AudioObjectGetPropertyData(aggID, &prop, 0, NULL, &size, &currentList);
    if (err != noErr || currentList == NULL) {
        return -1;
    }
    
    CFMutableArrayRef newList = CFArrayCreateMutable(kCFAllocatorDefault, 0, &kCFTypeArrayCallBacks);
    CFArrayAppendValue(newList, targetUID);
    
    size = sizeof(newList);
    err = AudioObjectSetPropertyData(aggID, &prop, 0, NULL, size, &newList);
    
    CFRelease(newList);
    
    if (err != noErr) {
        return -1;
    }
    
    system("killall coreaudiod 2>/dev/null");
    sleep(2);
    
    return 0;
}

void set_default_input(AudioDeviceID deviceID) {
    AudioObjectPropertyAddress prop = {
        kAudioHardwarePropertyDefaultInputDevice,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMain
    };
    
    UInt32 size = sizeof(deviceID);
    AudioObjectSetPropertyData(kAudioObjectSystemObject, &prop, 0, NULL, size, &deviceID);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <aggregate-name> <mic-name>\n", argv[0]);
        return 1;
    }
    
    const char *aggName = argv[1];
    const char *micName = argv[2];
    
    AudioDeviceID aggID = find_device_by_name(aggName);
    if (aggID == kAudioDeviceUnknown) {
        return 1;
    }
    
    AudioDeviceID micID = find_device_by_name(micName);
    if (micID == kAudioDeviceUnknown) {
        return 1;
    }
    
    CFStringRef micUID = get_device_uid(micID);
    if (!micUID) {
        return 1;
    }
    
    if (set_aggregate_to_single_device(aggID, micUID) != 0) {
        CFRelease(micUID);
        return 1;
    }
    
    CFRelease(micUID);
    set_default_input(micID);
    
    return 0;
}
