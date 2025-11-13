/** List Microphones command implementation. */
import { useState, useEffect } from "react";
import { List, ActionPanel, Action, Icon } from "@raycast/api";
import { executeCliCommand, showErrorToast, showSuccessToast } from "./utils";
import { ListSourcesResponse, ErrorResponse, AudioSource } from "./types";

export default function ListMicrophones() {
  const [sources, setSources] = useState<AudioSource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchText, setSearchText] = useState("");

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
      } else if (response.success) {
        await showSuccessToast(response.message);
        // Reload sources to reflect any changes
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
        // Debounce search - reload after user stops typing
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
        sources.map((source) => (
          <List.Item
            key={`${source.index}-${source.name}`}
            title={source.name}
            subtitle={`Index: ${source.index}`}
            icon={Icon.Microphone}
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
        ))
      )}
    </List>
  );
}
