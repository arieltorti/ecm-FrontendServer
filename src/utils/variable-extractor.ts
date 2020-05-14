/**
 * Finds the name of declared variables in the model.
 * The declarations must be of the form (param <VAR> <VALUE>), ignoring additional whitespaces
 *
 * TODO: Implement a parser and unparser instead of using Regex.
 */
const VARIABLES_REGEX = new RegExp(/^(?!;).*\(\s*param\s+(\w+)\s+.*\)/, "gm");

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Returns a new simulation model where the selected variable value is replaced
 * by the new value.
 *
 * @param {*} model Simulation model string
 * @param {*} variable Variable name
 * @param {*} value New value
 */
export function replaceModelVariableValue(
  model: string,
  variable: string,
  value: number
): string {
  const singleVariableRegex = new RegExp(
    `^(?!;)(.*\\(\\s*param\\s+${escapeRegExp(variable)}\\s+)(.*)\\s*(\\))`,
    "gm"
  );
  return model.replace(singleVariableRegex, `$1${value}$3`);
}

/**
 * Returns a list of the names of all declared variables on the model
 *
 * @param {*} model Simulation model string
 */
export function extractModelVariables(model: string): string[] {
  // We could use matchAll, but as we're not using a transpiler and someone may use this on IE11
  // we'll do it the old way instead.
  let match;
  const variables = [];
  while ((match = VARIABLES_REGEX.exec(model)) != null) {
    variables.push(match[1]);
  }
  return variables;
}
