<style src="./duplicationAffaire.css" scoped></style>
<template src="./duplicationAffaire.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler';
const moment = require("moment");

export default {
  name: "duplicationAffaire",
  props: {
    affaire: {type: Object}
  },
  components: {},
  data: () => ({
    showDuplicationAffaireForm: false,
    types_modifs_affaire_list: [],
    type_modif_affaire: null,
    affaire_numeros_anciens: [],
    affaire_numeros_nouveaux: [],
    selectedAnciensNumeros: null,
    selectedNouveauxNumeros: null
  }),

  methods: {
    /**
     * Open duplication affaire dialog
     */
    openDuplicationAffaireDialog() {
      this.searchAffaireNumeros();
      this.showDuplicationAffaireForm = true;
    },

    /*
    * Init types modifications affaire list
    */
    initTypesModifsAffaireList() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_TYPES_MODIF_AFFAIRE_ENDPOINT,
        {
          withCredentials: true,
          headers: {"Accept": "application/json"}
        }
      )
      .then(response =>{
        if (response && response.data) {
          this.types_modifs_affaire_list = response.data;

          if(this.types_modifs_affaire_list && this.types_modifs_affaire_list.length > 0){
            this.type_modif_affaire = this.types_modifs_affaire_list[0].id;
          }
        }
      })
      //Error
      .catch(err => {
        handleException(err, this);
      });
    },

    /*
     * SEARCH AFFAIRE NUMEROS
     */
    async searchAffaireNumeros() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT +
            this.$route.params.id + "?affaire_numero_actif=true",
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
           this.affaire_numeros_all = response.data;
            this.affaire_numeros_nouveaux = response.data.filter(
              x => x.affaire_numero_type_id === Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_NOUVEAU_ID)
            );
            this.affaire_numeros_anciens = response.data.filter(
              x => x.affaire_numero_type_id === Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID)
            );
            this.affaire_numeros_nouveaux.forEach(function(element) {
              if (element.numero_etat_id === Number(process.env.VUE_APP_NUMERO_ABANDONNE_ID)) {
                element.active = false;
              } else {
                element.active = true;
              }
            });
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },


    /*
    * Save duplicated affaire
    */
    saveDuplicatedAffaire(){
      let _this = this;

      //Duplicate affaire
      this.duplicateAffaire()
      .then(function(response){
        if(response && response.data && response.data.length > 0){
          var id_affaire_fille = response.data[0];

          //Save affaires modifications
          _this.saveAffaireModifications(id_affaire_fille);
        }
        else{
          handleException(null, _this);
        }

        _this.showDuplicationAffaireForm = false;


      })
      .catch(function(err){
        handleException(err, _this);
      });
    },

    /**
     * Duplicate affaire
     */
    duplicateAffaire(){
      var formData = this.initNewAffairePostData();

      return new Promise((resolve, reject) => {
        var url = process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRES_ENDPOINT;
        this.$http
        .post(url, formData, {
          withCredentials: true,
          headers: { Accept: "application/json" }
        })
        .then(response => resolve(response))
        .catch((err) => reject(err))
      });
    },

    /**
     * Init new affaire post data
     */
    initNewAffairePostData(){
      var formData = new FormData();
      formData.append("type_id", this.affaire.type_id);

      if (this.affaire.nom) {
        formData.append("nom", this.affaire.nom);
        }
      if (this.affaire.client_commande_id) {
        formData.append("client_commande_id", this.affaire.client_commande_id);
        }
      if (this.affaire.client_commande_complement) {
        formData.append("client_commande_complement", this.affaire.client_commande_complement);
        }
      if (this.affaire.client_envoi_id) {
        formData.append("client_envoi_id", this.affaire.client_envoi_id);
        }
      if (this.affaire.client_envoi_complement) {
        formData.append("client_envoi_complement", this.affaire.client_envoi_complement);
        }
      if (this.affaire.responsable_id && this.affaire.responsable_id !== "-") {
        formData.append("responsable_id", this.affaire.responsable_id);
        }
      if (this.affaire.technicien_id) {
        formData.append("technicien_id", this.affaire.technicien_id);
        }
      if (this.affaire.cadastre_id !== null && this.affaire.cadastre_id !== undefined) {
        formData.append("cadastre_id", this.affaire.cadastre_id);
      }
      if (this.affaire.localisation_e !== null && this.affaire.localisation_e !== undefined) {
        formData.append("localisation_E", this.affaire.localisation_e);
      } else {
        formData.append("localisation_E", 0);
      }
      if (this.affaire.localisation_n !== null && this.affaire.localisation_n !== undefined) {
        formData.append("localisation_N", this.affaire.localisation_n);
      } else {
        formData.append("localisation_N", 0);
      }
      if (this.affaire.vref) {
        formData.append("vref", this.affaire.vref);
      }
      if (this.affaire.chemin) {
        formData.append("chemin", this.affaire.chemin);
      }
      if (this.affaire.date_ouverture){
        formData.append("date_ouverture",
          moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_WS));
      }

      return formData;
    },

    /**
     * Save affaire modifications
     */
    saveAffaireModifications(id_affaire_fille){
      let _this = this;
      var formData = new FormData();
      formData.append("affaire_id_mere", this.affaire.id);
      formData.append("affaire_id_fille", id_affaire_fille);
      formData.append("type_id", this.type_modif_affaire);
      formData.append("date", moment(new Date(), process.env.VUE_APP_DATEFORMAT_CLIENT).format(process.env.VUE_APP_DATEFORMAT_WS));

      var url = process.env.VUE_APP_API_URL + process.env.VUE_APP_MODIFICATION_AFFAIRE_ENDPOINT;
        this.$http
        .post(url, formData, {
          withCredentials: true,
          headers: { Accept: "application/json" }
        })
        .then(response => {
          if (response && response.data) {
            this.deactivateAffaireNumeros(id_affaire_fille)
            .then(function(){
              _this.addAffaireNumerosAll(id_affaire_fille);
            })
            .catch(err => {
              handleException(err, _this);
            });
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Add affaire numero
     */
    addAffaireNumerosAll(id_affaire_fille){
      let _this = this;
      var promises = [];

      this.selectedAnciensNumeros.forEach((num) => {
          promises.push(this.addAffaireNumero(id_affaire_fille, num, process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID));
      });

      this.selectedNouveauxNumeros.forEach((num) => {
          promises.push(this.addAffaireNumero(id_affaire_fille, num, process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_NOUVEAU_ID));
      });

      Promise.all(promises)
      .then(response => {
        if (response) {
          _this.$root.$emit("ShowMessage", "L'affaire a été dupliquée avec succès");
          _this.$root.$emit("UpdateNumerosAffaires");
          this.searchAffaireNumeros();
        }
      })
      .catch(err => {
        handleException(err, this);
      });
    },

    /**
     * Add affaire numero
     */
    addAffaireNumero(id_affaire_fille, numero_id, type_id){
      var formData = new FormData();
      formData.append("affaire_id", id_affaire_fille);
      formData.append("numero_id", numero_id);
      formData.append("type_id", type_id);
      formData.append("actif", true);

      return new Promise((resolve, reject) => {
        var url = process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT;
        this.$http
        .post(url, formData, {
          withCredentials: true,
          headers: { Accept: "application/json" }
        })
        .then(response => resolve(response))
        .catch((err) => reject(err))
      });
    },


    /**
     * Deactivate numero_affaire in source affaire
     **/
    deactivateAffaireNumeros(id_affaire_fille){
      let numeros = [];
      this.selectedAnciensNumeros.forEach(num => {
         numeros.push(num);
      });

      this.selectedNouveauxNumeros.forEach((num) => {
        numeros.push(num);
      });

      if(numeros.length > 0){
        var formData = new FormData();
        formData.append("affaire_id", this.affaire.id);
        formData.append("affaire_destination_id", id_affaire_fille);
        formData.append("numeros", JSON.stringify(numeros));

        return new Promise((resolve, reject) => {
          var url = process.env.VUE_APP_API_URL + process.env.VUE_APP_DESACTIVER_AFFAIRE_NUMEROS_ENDPOINT;
          this.$http
          .post(url, formData, {
            withCredentials: true,
            headers: { Accept: "application/json" }
          })
          .then(response => resolve(response))
          .catch((err) => reject(err))
        });
      }
    },

    /**
     * Récupérer la sélection des anciens numéros
     */
    onSelectNumsAnciens(items) {
      this.selectedAnciensNumeros = items.map(x => (x.numero_id));
    },


    /**
     * Récupérer la sélection des nouveaux numéros
     */
    onSelectNumsNouveux(items) {
      this.selectedNouveauxNumeros = items.map(x => (x.numero_id));
    }
  },

  mounted: function() {
    this.initTypesModifsAffaireList();
  }
};
</script>



