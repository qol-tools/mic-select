import { useState, useEffect } from "react";
import { List, ActionPanel, Action, Icon } from "@raycast/api";
import { executeCliCommand, showErrorToast, showSuccessToast } from "./utils";
import { ListSourcesResponse, ErrorResponse, AudioSource } from "./types";
import { execSync } from "child_process";
import path from "path";

export default function ListMicrophones() {
  const [sources, setSources] = useState<AudioSource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchText, setSearchText] = useState("");
  const [currentMic, setCurrentMic] = useState<string>("");

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = async () => {
    setIsLoading(true);
    try {
      const args = ["list", "--limit", "50"];
      if (searchText.trim()) {
        args.push("--query", searchText.trim());
      }
      const response = executeCliCommand<ListSourcesResponse | ErrorResponse>(args);
      
      if ("error" in response) {
        await showErrorToast(response.error);
        setSources([]);
      } else {
        setSources(response.sources);
        try {
          const current = execSync("SwitchAudioSource -t input -c", { encoding: "utf-8" }).trim();
          setCurrentMic(current);
        } catch {
          setCurrentMic("");
        }
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      await showErrorToast(message);
      setSources([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwitch = async (source: AudioSource) => {
    try {
      const response = executeCliCommand<{ success: boolean; message: string } | ErrorResponse>([
        "switch",
        "--name",
        source.name,
      ]);

      if ("error" in response) {
        await showErrorToast(response.error);
        return;
      }
      
      if (response.success) {
        try {
          const toolPath = path.join(process.env.HOME || "", "repos/private/mic-select/macos/aggregate-mic");
          execSync(`"${toolPath}" "Aggregate Device" "${source.name}"`, { 
            encoding: "utf-8",
            timeout: 5000 
          });
        } catch {
        }
        
        await showSuccessToast(response.message);
        await loadSources();
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      await showErrorToast(message);
    }
  };


  return (
    <List
      isLoading={isLoading}
      searchBarPlaceholder="Search microphones..."
      onSearchTextChange={(text) => {
        setSearchText(text);
        const timeoutId = setTimeout(() => {
          loadSources();
        }, 300);
        return () => clearTimeout(timeoutId);
      }}
      throttle
    >
      {sources.length === 0 && !isLoading ? (
        <List.EmptyView
          icon={Icon.Microphone}
          title="No microphones found"
          description="Try adjusting your search query or check your audio system configuration."
        />
      ) : (
        <>
          <List.Section title="All Microphones">
            {sources.map((source) => (
              <List.Item
                key={`${source.index}-${source.name}`}
                title={source.name}
                subtitle={`Index: ${source.index}`}
                icon={Icon.Microphone}
                accessories={source.name === currentMic ? [{ text: "Current" }] : []}
                actions={
                  <ActionPanel>
                    <Action
                      title="Switch to This Microphone"
                      icon={Icon.ArrowRight}
                      onAction={() => handleSwitch(source)}
                    />
                    <Action
                      title="Refresh List"
                      icon={Icon.ArrowClockwise}
                      onAction={loadSources}
                      shortcut={{ modifiers: ["cmd"], key: "r" }}
                    />
                  </ActionPanel>
                }
              />
            ))}
          </List.Section>
        </>
      )}
    </List>
  );
}
