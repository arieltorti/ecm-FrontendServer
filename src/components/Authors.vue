<template>
  <div class="container">
    <span class="category">Authors:</span>
    <p class="names">
      Nicolás Morando (*), Mauricio Sanfilippo, Roberto Daniel Rabinovich (*),
      María de los Ángeles Pando (*).
    </p>

    <span class="category">Programmers:</span>
    <p class="names">
      Francisco Herrero, Matías Iturburu, Ariel Torti.
    </p>

    <span class="category">Acknowledgments:</span>
    <p class="names">
      <a href="https://cs.famaf.unc.edu.ar/~nicolasw/">Nicolás Wolovick (**)</a>
    </p>

    <div class="references">
      <span>
        <a href="http://www.inbirs.org.ar/"
          >* Instituto de Investigaciones Biomédicas en Retrovirus y SIDA</a
        ></span
      >

      <span>
        <a href="https://www.famaf.unc.edu.ar/"
          >** Facultad de Matemática, Astronomía, Física y Computación</a
        ></span
      >
    </div>
  </div>
</template>
<script>
export default {};
</script>

<style lang="sass" scoped>
.container
  margin: 1.5em 0

.names
  margin: 1em 3em

.category
  text-decoration: underline

.references span
  display: block
</style>
