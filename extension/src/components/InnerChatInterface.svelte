<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { chatMessages } from '../ts/stores';
  import { Sender } from '../ts/types';
  import { addUserInputListener, dispatchUserInput } from '../utils/chat';

  let userInputValue = '';
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
          <div class="system-message">{message.tokens.join('')}</div>
        {:else}
          <div class="user-message">{message.tokens.join('')}</div>
        {/if}
      </div>
    {/each}
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

