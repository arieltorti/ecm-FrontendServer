export function preciseRound(number: number, presicion = 7): number {
  return (
    Math.round((number + Number.EPSILON) * Math.pow(10, presicion)) /
    Math.pow(10, presicion)
  );
}
