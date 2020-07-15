/** Precisely rounds number based on the number of significant decimal places */
export function preciseRound(number, precision = 7) {
  return (
    Math.round((number + Number.EPSILON) * Math.pow(10, precision)) /
    Math.pow(10, precision)
  );
}
