<template>
  <div class="container">
    <h2 class="text-center">Instructions</h2>
    <section>
      <h3>Model Simulation</h3>
      <ol>
        <li>Click on the <b>Model</b> selection box</li>
        <li>Choose the desired model (e.g. SEIR 5G)</li>
        <li>
          Model equations will be shown in the <b>Model Details</b> section
          below
        </li>
        <li>
          On the <i>Simulation Parameters</i> section:
          <ul>
            <li>
              <div class="li-container">
                <h4>General</h4>
                <span>Enter the simulation time in days</span>
                <span>Enter the number of steps per day</span>
              </div>
            </li>

            <li>
              <div class="li-container">
                <h4>Initial conditions</h4>
                <span
                  >For each subpopulation (G1 to G5) enter the number of
                  susceptibles (S), Exposed (E), Infectious (I) and Resistant
                  (R)</span
                >
              </div>
            </li>

            <li>
              <div class="li-container">
                <h4>Params</h4>
                <span>Enter the values for p, gama (γ) and sigma (σ)</span>
                <span
                  >Range usage: the <i>range</i> button can be clicked and both
                  limits can be defined as desired</span
                >
                <span
                  >Enter the values of C (number of contacts per unit of time)
                  and N (number of individual on each subpopulation) for each
                  subpopulation (G1 to G5)</span
                >
              </div>
            </li>
          </ul>
        </li>

        <li>
          <div class="li-container">
            <span
              >In the <i>Simulation</i> section click the
              <b>Simulate</b> button</span
            >
            <span>Graphs that correspond to S, E, I, R totals will appear</span>
          </div>
        </li>

        <li>
          To visualize a specific subpopulation click on the corresponding
          checkbox
        </li>

        <li>
          <div class="li-container">
            <span
              >Hovering the mouse on each line of the graph will show the values
              of the selected spot (the graph can be zoomed in and out)</span
            >
            <span
              >If a range value was used an slider will be shown below the
              graph</span
            >
          </div>
        </li>

        <li>
          Moving the slider dot will show the corresponding graph on real time
        </li>

        <li>
          In order to obtain the generated S, E, I, R values during the whole
          simulation the <b>Download CSV</b> can be clicked to download a comma
          separated value file containing their values
        </li>

        <li>
          To visualize the downloaded file, open a new Excel File, go to the
          "Data" tab, inside "Get external data" select "From text", locate the
          folder in which the .csv file is stored and select it, the text import
          assitant will be opened. On step 1 click "Next", on step 2 check
          "Comma" on "Separators", on step 3 go to "Advanced" and enter a dot
          (".") as the decimal separator and a comma (",") as the thousands
          separator, then click "Accept" and "End"
        </li>
      </ol>
    </section>

    <section>
      <h3>R estimation</h3>

      <ol>
        <li>Click on the "Ro calculator" tab</li>
        <li>Enter the values for p and gamma (γ)</li>
        <li>
          On the text box labeled "S" enter the number of susceptibles at a
          moment of time when the value of R(t)/Re will be calculated
        </li>
        <li>
          For each subpopulation enter the number of individuals and the number
          of daily contacts for each type of contact on the corresponding text
          boxes
        </li>
        <li>
          On the right of each line the number of contacts for each
          subpopulation will be shown
        </li>
        <li>
          On the <i>Results</i> section the values for population's N,
          population contacts mean, R0 and R(t) will be shown
        </li>
      </ol>
    </section>
  </div>
</template>
<script>
export default {};
</script>

<style lang="sass" scoped>
.container
  margin: 1.5em 0

.text-center
  text-align: center

.li-container
  h4
    margin: .5em 0

  span
    display: block
</style>
