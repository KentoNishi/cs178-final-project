// CODE POINTER: These two types are key to the 'message' concept. We define the two types of messages that are possible
// (the backend has a third type due to openAI's API, but otherwise messages are split into these two categories).
export enum Sender {
  System = "system",
  User = "user",
}
// Each message has both the actual message (stored by `tokens`), and the type of message, identified by `sender`.
export interface Message {
  tokens: string[];
  sender: Sender;
}

export type ChatInputCallback = (message: string) => void;

// CODE POINTER: The frontend definition of an Artifact type (ArtifactContent, since it doesn't have the methods
// of the main Artifact type in the backend, but otherwise they are identical, allowing for easy passing between
// frontend and backend).
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
