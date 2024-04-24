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