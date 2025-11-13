import { execSync } from "child_process";
import { findPythonExecutable, executeCliCommand, parseJsonOutput } from "./utils";

jest.mock("child_process");
const mockedExecSync = execSync as jest.MockedFunction<typeof execSync>;

describe("findPythonExecutable", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should find python3 in common paths", () => {
    mockedExecSync.mockImplementation((command) => {
      if (command === '"/usr/bin/python3" --version') {
        return "Python 3.11.0" as any;
      }
      throw new Error("Command failed");
    });

    const result = findPythonExecutable();
    expect(result).toBe("/usr/bin/python3");
  });

  it("should try multiple paths", () => {
    let callCount = 0;
    mockedExecSync.mockImplementation((command) => {
      callCount++;
      if (command === '"/opt/homebrew/bin/python3" --version') {
        return "Python 3.11.0" as any;
      }
      throw new Error("Command failed");
    });

    const result = findPythonExecutable();
    expect(result).toBe("/opt/homebrew/bin/python3");
    expect(callCount).toBeGreaterThan(1);
  });

  it("should fall back to which python3", () => {
    mockedExecSync.mockImplementation((command) => {
      if (command === "which python3") {
        return "/custom/path/python3\n" as any;
      }
      throw new Error("Command failed");
    });

    const result = findPythonExecutable();
    expect(result).toBe("/custom/path/python3");
  });

  it("should throw error when python3 is not found", () => {
    mockedExecSync.mockImplementation(() => {
      throw new Error("Command failed");
    });

    expect(() => findPythonExecutable()).toThrow(
      "Python 3 not found. Please ensure Python 3 is installed and available in PATH."
    );
  });
});

describe("parseJsonOutput", () => {
  it("should parse valid JSON", () => {
    const input = '{"sources": [{"name": "Test Mic", "index": 0}]}';
    const result = parseJsonOutput(input);
    expect(result).toEqual({ sources: [{ name: "Test Mic", index: 0 }] });
  });

  it("should trim whitespace before parsing", () => {
    const input = '\n  {"value": 42}  \n';
    const result = parseJsonOutput(input);
    expect(result).toEqual({ value: 42 });
  });

  it("should throw error for invalid JSON", () => {
    const input = "not json";
    expect(() => parseJsonOutput(input)).toThrow("Failed to parse JSON output");
  });

  it("should throw error for empty string", () => {
    const input = "";
    expect(() => parseJsonOutput(input)).toThrow("Failed to parse JSON output");
  });
});

describe("executeCliCommand", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should execute CLI command and parse JSON output", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any) // findPython
      .mockImplementationOnce(() =>
        '{"sources": [{"name": "Test Mic", "index": 0}]}' as any
      );

    const result = executeCliCommand<{ sources: Array<{ name: string; index: number }> }>([
      "list",
      "--limit",
      "5",
    ]);

    expect(result).toEqual({
      sources: [{ name: "Test Mic", index: 0 }],
    });
  });

  it("should handle list command with query", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() =>
        '{"sources": [{"name": "USB Mic", "index": 1}]}' as any
      );

    const result = executeCliCommand(["list", "--query", "USB", "--limit", "10"]);
    expect(result).toHaveProperty("sources");
  });

  it("should handle switch command", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() =>
        '{"success": true, "message": "Switched to USB Mic"}' as any
      );

    const result = executeCliCommand<{ success: boolean; message: string }>([
      "switch",
      "--name",
      "USB Mic",
    ]);

    expect(result).toEqual({
      success: true,
      message: "Switched to USB Mic",
    });
  });

  it("should throw error when Python is not found", () => {
    mockedExecSync.mockImplementation(() => {
      const error: any = new Error("ENOENT");
      error.code = "ENOENT";
      throw error;
    });

    expect(() => executeCliCommand(["list"])).toThrow(
      "Python 3 not found. Please ensure Python 3 is installed and available in PATH."
    );
  });

  it("should throw error with stderr information", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() => {
        const error: any = new Error("Command failed");
        error.stderr = "Audio device not found";
        throw error;
      });

    expect(() => executeCliCommand(["switch", "--name", "NonExistent"])).toThrow(
      "CLI execution failed"
    );
  });

  it("should handle invalid JSON output", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() => "not valid json" as any);

    expect(() => executeCliCommand(["list"])).toThrow();
  });

  it("should respect maxBuffer option", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce((_command, options: any) => {
        expect(options.maxBuffer).toBe(1024 * 1024);
        return '{"sources": []}' as any;
      });

    executeCliCommand(["list"]);
  });

  it("should handle error responses from CLI", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() =>
        '{"error": "No audio devices found"}' as any
      );

    const result = executeCliCommand<{ error: string }>(["list"]);
    expect(result).toEqual({ error: "No audio devices found" });
  });
});

describe("CLI Integration", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("should handle complete list workflow", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() =>
        JSON.stringify({
          sources: [
            { name: "Mic 1", index: 0 },
            { name: "Mic 2", index: 1 },
          ],
        }) as any
      );

    const result = executeCliCommand<{
      sources: Array<{ name: string; index: number }>;
    }>(["list", "--limit", "50"]);

    expect(result.sources).toHaveLength(2);
    expect(result.sources[0].name).toBe("Mic 1");
  });

  it("should handle complete switch workflow", () => {
    mockedExecSync
      .mockImplementationOnce(() => "Python 3.11.0" as any)
      .mockImplementationOnce(() =>
        JSON.stringify({
          success: true,
          message: "Successfully switched to Mic 2",
        }) as any
      );

    const result = executeCliCommand<{ success: boolean; message: string }>([
      "switch",
      "--name",
      "Mic 2",
    ]);

    expect(result.success).toBe(true);
    expect(result.message).toContain("Mic 2");
  });
});
