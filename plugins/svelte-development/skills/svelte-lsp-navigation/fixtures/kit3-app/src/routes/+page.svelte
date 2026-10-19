<script lang="ts">
  import CounterButton from "#lib/components/CounterButton.svelte";
  import { Counter } from "#lib/counter.svelte.js";
  import { formatCount } from "#lib/format.js";

  let { data } = $props();
  const counter = new Counter();
</script>

<h1>{data.title}</h1>

<!-- Deliberate type error for the svelte-lsp-navigation examples: label must be a string. -->
<CounterButton {counter} label={42}>
  <p>Doubled: {formatCount(counter.doubled)}</p>
</CounterButton>

<button type="button" onclick={() => counter.reset()}>Reset</button>
