/** Mock for @raycast/api */

export const Toast = {
  Style: {
    Success: "success",
    Failure: "failure",
    Animated: "animated",
  },
};

export async function showToast(options: {
  style: string;
  title: string;
  message?: string;
}): Promise<void> {
  // Mock implementation
  return Promise.resolve();
}

export const Icon = {
  Microphone: "microphone",
  ArrowRight: "arrow-right",
  ArrowClockwise: "arrow-clockwise",
};

export const List = () => null;
export const ActionPanel = () => null;
export const Action = () => null;
