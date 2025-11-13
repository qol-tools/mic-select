import { execSync } from "child_process";
import { showToast, Toast } from "@raycast/api";
import { join } from "path";

function getCliScriptPath(): string {
  let currentPath = __dirname;

  for (let i = 0; i < 5; i++) {
    const cliPath = join(currentPath, "raycast_cli.py");
    try {
      execSync(`test -f "${cliPath}"`, { stdio: "ignore" });
      return cliPath;
    } catch {
      currentPath = join(currentPath, "..");
    }
  }

  const fallbackPaths = [
    join(__dirname, "..", "raycast_cli.py"),
    join(__dirname, "..", "..", "raycast_cli.py"),
    join(__dirname.replace(/\/dist.*$/, ""), "raycast_cli.py"),
    join(__dirname.replace(/\/src.*$/, ""), "raycast_cli.py"),
  ];

  for (const cliPath of fallbackPaths) {
    try {
      execSync(`test -f "${cliPath}"`, { stdio: "ignore" });
      return cliPath;
    } catch {
      continue;
    }
  }

  return fallbackPaths[0];
}

const CLI_SCRIPT_PATH = getCliScriptPath();

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
      continue;
    }
  }

  try {
    const result = execSync("which python3", { encoding: "utf-8" }).trim();
    if (result) {
      return result;
    }
  } catch {}

  throw new Error(
    "Python 3 not found. Please ensure Python 3 is installed and available in PATH."
  );
}

export function executeCliCommand<T>(args: string[]): T {
  const python = findPythonExecutable();

  const quotedArgs = args.map(arg => {
    if (arg.includes(" ") || arg.includes("'") || arg.includes('"')) {
      return `"${arg.replace(/"/g, '\\"')}"`;
    }
    return arg;
  });

  const command = [python, `"${CLI_SCRIPT_PATH}"`, ...quotedArgs];

  try {
    const output = execSync(command.join(" "), {
      encoding: "utf-8",
      maxBuffer: 1024 * 1024,
    });

    return JSON.parse(output.trim()) as T;
  } catch (error: unknown) {
    if (error instanceof Error) {
      if (error.message.includes("ENOENT") || error.message.includes("not found")) {
        throw new Error(
          `CLI script not found at: ${CLI_SCRIPT_PATH}\nPython: ${python}\nPlease run 'make install' to set up the extension.`
        );
      }
      const stderr = (error as any).stderr || "";
      const stdout = (error as any).stdout || "";
      const errorMessage = stderr || stdout || error.message;
      throw new Error(`CLI execution failed: ${errorMessage}\nScript: ${CLI_SCRIPT_PATH}`);
    }
    throw new Error(`CLI execution failed: ${String(error)}`);
  }
}

export function parseJsonOutput<T>(output: string): T {
  try {
    return JSON.parse(output.trim()) as T;
  } catch (error) {
    throw new Error(`Failed to parse JSON output: ${error}`);
  }
}

export async function showErrorToast(message: string): Promise<void> {
  await showToast({
    style: Toast.Style.Failure,
    title: "Error",
    message,
  });
}

export async function showSuccessToast(message: string): Promise<void> {
  await showToast({
    style: Toast.Style.Success,
    title: "Success",
    message,
  });
}
