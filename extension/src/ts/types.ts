export enum Sender {
  System = "system",
  User = "user",
}

export interface Message {
  tokens: string[];
  sender: Sender;
}

export type ChatInputCallback = (message: string) => void;

export interface ArtifactContent {
  query_message     : string;
  prompts           : string[];
  response_objects  : string[];
  response_contents : string[];
  references        : string[][];
  answer            : string;
}

export interface Filters {
  "num_embeds"      : number,
  "termDescription" : string,
  "catalogSubject"  : string
}

export interface ClientMessage {
  artifact: ArtifactContent,
  // filters: Filters
}
export enum BackendState {
  Generating = "generating",
  Default = "default",
  Error = "error",
};
