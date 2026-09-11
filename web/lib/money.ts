/** Whole-dollar formatting everywhere in Finance -- cents are noise for
 * the decisions this module surfaces (a budget, a savings goal, a
 * monthly trend), and mixing precision levels across cards looks like a
 * bug even when it isn't. */
export function formatMoney(amount: number, currency = "AUD"): string {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatSignedMoney(amount: number, currency = "AUD"): string {
  const formatted = formatMoney(Math.abs(amount), currency);
  return amount < 0 ? `-${formatted}` : formatted;
}
