<style src="./operateurs.css" scoped></style>
<template src="./operateurs.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler'
import {checkPermission} from '@/services/helper'

export default {
  name: 'Operateurs',
  props: {},
  data: () => ({
      operateurs: [],
      deleteOperateurActive: false,
      deleteMessage: '',
      currentDeleteId: null,
      editionOperateursAllowed: false,
      search: {
        nom: null,
        prenom: null,
        login: null
      }
  }),
  methods: {
        /**
         * Search operateurs
        */
        async searchOperateurs () {
          var formData = new FormData();
          if(this.search.nom)
            formData.append("nom", this.search.nom);

          if(this.search.prenom)
            formData.append("prenom", this.search.prenom);

          if(this.search.login)
            formData.append("login", this.search.login);

          this.$http.post(
            process.env.VUE_APP_API_URL + process.env.VUE_APP_SEARCH_OPERATEURS_ENDPOINT, 
            formData,
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          )
          .then(response =>{
            if(response && response.data){
              this.operateurs = response.data;
            }
          })
          //Error 
          .catch(err => {
            handleException(err, this);  
          })
        },

        /**
         * Clear the form
         */
        clearForm () {
          this.search.nom = null;
          this.search.prenom = null;
          this.search.login = null;
        },


        /**
         * Call edit operateur
         */
        callEditOperateur (id) {
         this.$router.push({ name: "OperateursEdit", params: { id: id } }) ; 
        },
        
        /**
         * Call delete operateur
         */
        callDeleteOperateur (id, nom, prenom) {
          this.currentDeleteId = id;

          if(prenom && nom)
            this.deleteMessage = prenom + ' ' + nom;
          else if(nom)
            this.deleteMessage = nom;
          else
            this.deleteMessage = "-";

          this.deleteMessage = "Confirmer la suppression de l'operateur '<strong>" + this.deleteMessage + "<strong>' ?";

          this.deleteOperateurActive = true;
        },

        /**
        * Delete operateur
        */
        onConfirmDelete () {

          /*var formData = new FormData();
          
          if(this.currentDeleteId)
            formData.append("id", this.currentDeleteId);*/

          this.$http.delete(
            process.env.VUE_APP_API_URL + process.env.VUE_APP_OPERATEURS_ENDPOINT + "?id=" +  this.currentDeleteId, 
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          )
          .then(response =>{
            if(response && response.data){
              this.searchOperateurs();
            }
          })
          //Error 
          .catch(err => {
            handleException(err, this);  
          })
        },


        /**
        * Import AD users
        */
        importADUsers () {
          this.$http.get(
            process.env.VUE_APP_API_URL + process.env.VUE_APP_ADD_OPERATEURS_AD_ENDPOINT, 
            {
              withCredentials: true,
              headers: {"Accept": "application/json"}
            }
          )
          .then(response =>{
            if(response && response.data && response.data.count && response.data.count > 0){
              this.$root.$emit("ShowMessage", response.data.count + " opérateurs importés avec succès depuis l'AD");
              this.searchOperateurs();
            }
            else{
              handleException(response, this);  
            }
          })
          //Error 
          .catch(err => {
            handleException(err, this);  
          })
        },

        /**
        * Cancel Delete operateur
        */
        onCancelDelete () {
          this.currentDeleteId = null;
        }
  },

  mounted: function(){
    this.searchOperateurs();
    this.editionOperateursAllowed = checkPermission(process.env.VUE_APP_FONCTION_ADMIN);
  }
}
</script>

