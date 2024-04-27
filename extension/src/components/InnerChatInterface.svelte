<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { Sender, type ArtifactContent, type ClientMessage, BackendState } from '../ts/types';
  import { chatMessages, backendState } from '../ts/stores';
  import { SyncLoader } from 'svelte-loading-spinners';
  import { dispatchUserInput, addUserInputListener, initializeNewSystemMessage } from '../utils/chat';
  import SvelteMarkdown from 'svelte-markdown';

  let userInputValue = '';
  let artifact : ArtifactContent = {
    query_message     : "",
    prompts           : [],
    response_objects  : [],
    response_contents : [],
    references        : [],
    answer            : ""
  };


  // Adding input listener to call API upon user input
  addUserInputListener(async (str) => {
    artifact.query_message = str;

    const client_message : ClientMessage = {
      artifact: artifact,
      // filters: {
      //   // TODO: Use these properly from the UI
      //   // I think num_embeds should be a dropdown or small 3 buttons with only one selectable at once with opts 3, 5, 10
      //   // termDescription and catalogSubject (think we should add ~2 more) would be dropdowns
      //   // I think the content for these should be established via a 'handshake' API call to the backend to populate these upon page load
      //   "num_embeds": 3,
      //   "termDescription": "",
      //   "catalogSubject": ""
      // }
    };
    $backendState = BackendState.Generating;
    fetch("http://127.0.0.1:8000/recommend", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(
        client_message
      )
    })
    .then(response => {
      if (!response.ok) {
        backendState.set(BackendState.Error);
        throw new Error('Network response was not ok');
      }
      backendState.set(BackendState.Default);
      return response.json();
    })
    .then(data => {
      backendState.set(BackendState.Default);
      // For now, just creating new system message with the whole result. Work on streaming to come
      artifact = data;

      console.log(data);
      initializeNewSystemMessage(data.answer);
    })
    .catch(error => {
      backendState.set(BackendState.Error);
      console.error('Fetch error:', error);
    });
  })

  const onUserInput = () => {
    if (userInputValue.trim() === '') {
      return;
    }

    dispatchUserInput(userInputValue);
    userInputValue = '';
  };

  let scrollTarget: HTMLDivElement;

  const scrollToBottom = async () => {
    await tick();
    if (scrollTarget) scrollTarget.scrollTop = scrollTarget.scrollHeight;
  };

  $: if ($chatMessages) {
    scrollToBottom();
  }
</script>

<div class="split-wrapper">
  <div class="title">Untitled Chat</div>
  <div class="message-scroller" bind:this={scrollTarget}>
    {#each $chatMessages as message, i}
      <div class="message" class:system={message.sender === Sender.System} class:user={message.sender === Sender.User}>
        {#if message.sender === Sender.System}
          <div class="system-message">
            <SvelteMarkdown source={message.tokens.join('')} />
          </div>
        {:else}
          <div class="user-message">{message.tokens.join('')}</div>
        {/if}
      </div>
    {/each}
    {#if $backendState === BackendState.Generating}
      <div class="message">
        <div class="system-message" style="transform: scale({24 / 60});">
          <SyncLoader color="#FFFFFF" size="60" unit="px" />
        </div>
      </div>
    {/if}
  </div>
  <div class="message-input">
    <input type="text" class="textbox" placeholder="Type a message..." bind:value={userInputValue} on:keydown={(e) => {
      if (e.key === 'Enter') {
        onUserInput();
      }
    }} />
    <button class="material-symbols-outlined send-button" on:click|preventDefault={onUserInput}>send</button>
  </div>
</div>

<style>
  .split-wrapper {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: 12px 0px 12px 12px;
  }

  .title {
    height: 48px;
    font-weight: bold;
  }

  .message-scroller {
    flex: 1;
    overflow-y: scroll;
  }

  .split-wrapper {
    height: 100%;
  }

  .message {
    margin-bottom: 12px;
    display: flex;
    justify-content: flex-start;
  }

  .message>div {
    padding: 8px 12px;
    border-radius: 12px;
    max-width: 80%;
  }

  .system-message {
    background-color: var(--color-primary);
    color: white;
    float: left;
    white-space: pre-wrap;
    transform-origin: top left;
  }

  :global(ul, ol) {
    margin: 1rem;
  }

  .user-message {
    background-color: #f0f0f0;
    color: black;
    float: right;
  }

  .message.user {
    justify-content: flex-end;
  }

  .message-input {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #b0b0b0;
    padding-top: 12px;
    margin-right: 12px;
  }

  .textbox {
    flex: 1;
    padding: 8px 12px;
    border-radius: 20px 0px 0px 20px;
    border-right: 0px !important;
    height: 40px;
  }

  .send-button {
    padding: 8px 12px;
    border-radius: 0px 20px 20px 0px;
    background-color: var(--color-primary);
    color: white;
    cursor: pointer;
    border-left: 0px !important;
    height: 40px;
    vertical-align: middle;
    text-align: center;
    padding: 5px 10px;
  }

  .textbox, .send-button {
    border-color: #b0b0b0;
    border-width: 1px;
    border-style: solid;
  }
</style>

