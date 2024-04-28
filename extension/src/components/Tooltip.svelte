<script lang="ts">
  import { backendState, chatPanelOpen } from '../ts/stores';
  import { BackendState } from '../ts/types';
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div class="tooltip-content bg-secondary" on:click|preventDefault={() => {
  $backendState = BackendState.Default;
  $chatPanelOpen = true;
}}>
  Browse and discover courses with ChatGPT! 
  <a href="/" on:click|preventDefault style="margin-left: 12px;">
    Start Chat
  </a>
</div>
<style>
  .tooltip-content {
    padding: 4px 12px;
    border-radius: 40px;
    text-align: center;
    overflow: hidden;
    cursor: pointer;
    user-select: none;
  }
  .tooltip-content::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: var(--color-secondary) transparent transparent transparent;
  }
  a {
    color: white;
    text-decoration: underline;
    font-weight: bold;
  }
</style>
