import { Panel, PanelGroup } from "react-resizable-panels";
import { EvidenceInspector } from "../inspector/EvidenceInspector";
import { WorkspacePanel } from "../workspace/WorkspacePanel";
import { ResizeHandle } from "./ResizeHandle";
import { useMediaQuery } from "../../hooks/useMediaQuery";
import type { ChatMessage, ChunkMeta, Citation, LanguageCode } from "../../types/api";

interface ResizableWorkspaceProps {
  messages: ChatMessage[];
  language: LanguageCode;
  input: string;
  loading: boolean;
  indexReady: boolean;
  backendOnline: boolean;
  documentName: string | null;
  selectedCitationLabel?: string | null;
  selectedCitation: Citation | null;
  retrievedChunks: ChunkMeta[];
  onInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectCitation: (citation: Citation) => void;
  onSelectSuggestion: (text: string) => void;
  onSelectPassage: (chunk: ChunkMeta) => void;
  onDocumentUploaded: (name: string, text: string) => void;
  onDocumentClear: () => void;
}

const WIDE_LAYOUT_QUERY = "(min-width: 1024px)";

export function ResizableWorkspace(props: ResizableWorkspaceProps) {
  const isWide = useMediaQuery(WIDE_LAYOUT_QUERY);
  const showInspector = Boolean(props.selectedCitation) || props.retrievedChunks.length > 0;

  const workspace = (
    <WorkspacePanel
      messages={props.messages}
      language={props.language}
      input={props.input}
      loading={props.loading}
      indexReady={props.indexReady}
      backendOnline={props.backendOnline}
      documentName={props.documentName}
      selectedCitationLabel={props.selectedCitationLabel}
      onDocumentUploaded={props.onDocumentUploaded}
      onDocumentClear={props.onDocumentClear}
      onInputChange={props.onInputChange}
      onSubmit={props.onSubmit}
      onSelectCitation={props.onSelectCitation}
      onSelectSuggestion={props.onSelectSuggestion}
    />
  );

  const inspector = (
    <EvidenceInspector
      citation={props.selectedCitation}
      passages={props.retrievedChunks}
      language={props.language}
      sourceCount={props.retrievedChunks.length}
      onSelectPassage={props.onSelectPassage}
    />
  );

  const workspaceShell = <div className="h-full min-h-0 min-w-0">{workspace}</div>;

  if (!isWide) {
    return (
      <div className="flex h-full min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <div className="min-h-0 flex-1 overflow-hidden">{workspaceShell}</div>
        {showInspector && (
          <div className="h-[min(42vh,360px)] shrink-0 overflow-hidden border-t border-line">
            {inspector}
          </div>
        )}
      </div>
    );
  }

  if (!showInspector) {
    return <div className="h-full min-h-0 min-w-0 flex-1 overflow-hidden">{workspaceShell}</div>;
  }

  return (
    <PanelGroup
      direction="horizontal"
      autoSaveId="actlens-workspace"
      className="h-full min-h-0 min-w-0 flex-1"
    >
      <Panel defaultSize={58} minSize={36} className="min-h-0 min-w-0">
        {workspaceShell}
      </Panel>
      <ResizeHandle />
      <Panel defaultSize={42} minSize={28} maxSize={50} className="min-h-0 min-w-0">
        <div className="h-full min-h-0 overflow-hidden">{inspector}</div>
      </Panel>
    </PanelGroup>
  );
}
