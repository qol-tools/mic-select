/** Utility functions for Raycast extension. */
import { execSync } from "child_process";
import { showToast, Toast } from "@raycast/api";
import { join } from "path";

// Calculate path to CLI script relative to extension root
function getCliScriptPath(): string {
  // In Raycast, __dirname points to the compiled JS location
  // We need to go up to the project root, then to macos/cli
  const extensionRoot = __dirname.replace(/\/dist\/src$/, "").replace(/\/src$/, "");
  return join(extensionRoot, "..", "macos", "cli", "raycast_cli.py");
}

const CLI_SCRIPT_PATH = getCliScriptPath();

/**
 * Find Python 3 executable.
 */
export function findPythonExecutable(): string {
  const paths = [
    "/usr/bin/python3",
    "/usr/local/bin/python3",
    "/opt/homebrew/bin/python3",
  ];

  for (const path of paths) {
    try {
      execSync(`"${path}" --version`, { stdio: "ignore" });
      return path;
    } catch {
      // Continue searching
    }
  }

  // Try which as fallback
  try {
    const result = execSync("which python3", { encoding: "utf-8" }).trim();
    if (result) {
      return result;
    }
  } catch {
    // Fallback failed
  }

  throw new Error(
    "Python 3 not found. Please ensure Python 3 is installed and available in PATH."
  );
}

/**
 * Execute CLI command and return parsed JSON.
 */
export function executeCliCommand<T>(args: string[]): T {
  const python = findPythonExecutable();
  const command = [python, CLI_SCRIPT_PATH, ...args];

  try {
    const output = execSync(command.join(" "), {
      encoding: "utf-8",
      maxBuffer: 1024 * 1024, // 1MB
    });

    return JSON.parse(output.trim()) as T;
  } catch (error: unknown) {
    if (error instanceof Error) {
      if (error.message.includes("ENOENT") || error.message.includes("not found")) {
        throw new Error(
          `Python 3 not found. Please ensure Python 3 is installed and available in PATH.`
        );
      }
      // Try to extract stderr if available
      const errorMessage = (error as any).stderr 
        ? `${error.message}: ${(error as any).stderr}`
        : error.message;
      throw new Error(`CLI execution failed: ${errorMessage}`);
    }
    throw new Error(`CLI execution failed: ${String(error)}`);
  }
}

/**
 * Parse and validate JSON output from CLI.
 */
export function parseJsonOutput<T>(output: string): T {
  try {
    return JSON.parse(output.trim()) as T;
  } catch (error) {
    throw new Error(`Failed to parse JSON output: ${error}`);
  }
}

/**
 * Show error toast notification.
 */
export async function showErrorToast(message: string): Promise<void> {
  await showToast({
    style: Toast.Style.Failure,
    title: "Error",
    message,
  });
}

/**
 * Show success toast notification.
 */
export async function showSuccessToast(message: string): Promise<void> {
  await showToast({
    style: Toast.Style.Success,
    title: "Success",
    message,
  });
}
