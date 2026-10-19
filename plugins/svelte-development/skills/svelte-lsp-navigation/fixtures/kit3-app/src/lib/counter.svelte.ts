import type { Resettable } from "#lib/resettable.js";

/** Shared counter state: implements Resettable. */
export class Counter implements Resettable {
  count = $state(0);
  doubled = $derived(this.count * 2);

  increment(): void {
    this.count += 1;
  }

  reset(): void {
    this.count = 0;
  }
}
