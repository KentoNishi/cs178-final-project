import json
from Common import ArtifactContent

class Artifact:
    """
    Artifact class to store the prompts, responses, and references for a given query message.
    """

    def __init__(self, query_message, prompt, response, references) -> None:
        self.query_message    : str        = query_message

        # CODE POINTER: The artifact object really helps maintain the `session` concept on the backend.
        # it's within artifacts that the whole user's history is stored, between the `prompts`, `response_contents`,
        # `response_objects` and `references`, you have a strong history of all exchanges in each session.

        self.prompts          : list[str]  = [prompt]
        self.response_objects              = [response.model_dump_json()]
        self.response_contents: list[str]  = [response.choices[0].message.content]
        self.references = references
        self.answer = None

    def __str__(self) -> str:
        """
        Override __str__ to print the Artifact object as a JSON string.

        Returns:
            str: JSON string representation of the Artifact object.
        """
        return json.dumps(
            {
                "query_message": self.query_message,
                "answer": self.answer,
                "prompts": self.prompts,
                "response_contents": self.response_contents,
                "response_objects": self.response_objects,
                "references": self.references,
            },
            indent=4,
        )

    def get_latest_prompt(self) -> str:
        """
        Get the latest prompt.

        Returns:
            str: the latest prompt.
        """
        return self.prompts[-1]

    def get_latest_response(self) -> str:
        """
        Get the latest response.

        Returns:
            str: the latest response.
        """
        return self.response_contents[-1]

    def get_references(self) -> list:
        """
        Get the references for the query message.

        Returns:
            list: the references for the query message.
        """

        return self.references

    def get_answer(self) -> str:
        """
        Get the answer for the query message.

        Returns:
            str: the answer for the query message.
        """

        return self.answer

    def set_answer(self, answer: str) -> None:
        """
        Set the answer for the query message.

        Args:
            answer (str): the answer for the query message.
        """

        self.answer = answer

    def append(self, prompt: str, response) -> None:
        """
        Append a prompt and response to the artifact.

        Args:
            prompt (str): prompt to append
            response (openai.ChatCompletion): response object from OpenAI ChatCompletion API
        """

        self.prompts.append(prompt)
        self.response_objects.append(response.model_dump_json())
        self.response_contents.append(response.choices[0].message.content)

    def dump(self) -> dict:
        """
        Dump the Artifact object as a dictionary.

        Returns:
            dict: dictionary representation of the Artifact object.
        """

        return {
            "query_message": self.query_message,
            "prompts": self.prompts,
            "response_contents": self.response_contents,
            "response_objects": self.response_objects,
            "references": self.references,
            "answer": self.answer
        }

    def to_artifact_content(self) -> ArtifactContent:
        """
        Dump the Artifact object as an ArtifactContent object.
        """

        return ArtifactContent(
            query_message= self.query_message,
            prompts= self.prompts,
            response_contents= self.response_contents,
            response_objects= self.response_objects,
            references= self.references,
            answer= self.answer if self.answer else ""
        )