<style src="./numeros.css" scoped></style>
<template src="./numeros.html"></template>


<script>
import {
  getCadastres,
  getTypesNumeros,
  getEtatsNumeros
} from "@/services/helper";
import {handleException} from '@/services/exceptionsHandler'

export default {
  name: "Numeros",
  props: {},
  data: () => ({
    numeros: [],
    cadastre_liste: [],
    types_numeros: [],
    etats_numeros: [],
    search: {
      numero: null,
      suffixe: null,
      cadastre: "",
      type: "",
      etat: "",
      matDiff: false,
    }
  }),

  methods: {
    /*
     * SEARCH NUMEROS
     */
    async searchNumeros() {
      var formData = new FormData();
      if (this.search.numero) {
        formData.append("numero", this.search.numero);
      }
      if (this.search.suffixe) {
        formData.append("suffixe", this.search.suffixe);
      }
      if (this.search.cadastre) {
        formData.append("cadastre_id", this.search.cadastre.id);
      }
      if (this.search.type) {
        formData.append("type_numero_id", this.search.type.id);
      }
      if (this.search.etat) {
        formData.append("etat_id", this.search.etat.id);
      }
      if (this.search.matDiff) {
        formData.append("matDiff", this.search.matDiff);
      }

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_RECHERCHE_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response && response.data) {
            this.numeros = response.data;
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Init Cadastres list
     */
    initCadastresList() {
      getCadastres()
        .then(response => {
          if (response && response.data) {
            this.cadastre_liste = response.data.map(x => ({
              id: x.id,
              nom: x.nom,
              toLowerCase: () => x.nom.toLowerCase(),
              toString: () => x.nom
            }));
          }
        })

        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Init Types Numeros list
     */
    async initTypesNumerosList() {
      getTypesNumeros()
        .then(response => {
          if (response && response.data) {
            this.types_numeros = response.data.map(x => ({
              id: x.id,
              nom: x.nom,
              toLowerCase: () => x.nom.toLowerCase(),
              toString: () => x.nom
            }));
          }
        })

        .catch(err => {
          handleException(err, this);
        });
    },

    /*
     * Init Etats Numeros list
     */
    async initEtatsNumerosList() {
      getEtatsNumeros()
        .then(response => {
          if (response && response.data) {
            this.etats_numeros = response.data.map(x => ({
              id: x.id,
              nom: x.nom,
              toLowerCase: () => x.nom.toLowerCase(),
              toString: () => x.nom
            }));
          }
        })

        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Clear the form
     */
    clearForm() {
      this.search.numero = null;
      this.search.suffixe = null;
      this.search.cadastre = "";
      this.search.type = "";
      this.search.etat = "";
      this.matDiff = false;
    },

    /*
     * Open numéro in new tab
     */
    doOpenNumero(id) {
      this.$router.push({ name: "NumerosHistory", params: {id}});
    }
  },

  mounted: function() {
    this.initCadastresList();
    this.initTypesNumerosList();
    this.initEtatsNumerosList();
    this.searchNumeros();
  }
};
</script>

