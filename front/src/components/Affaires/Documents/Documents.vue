<style src="./documents.css" scoped></style>
<template src="./documents.html"></template>


<script>
import {handleException} from '@/services/exceptionsHandler'
import axios from "axios";
import {checkPermission} from '@/services/helper';

export default {
  name: "Documents",
  props: {},
  components: {},
  data: () => ({
    showUploadDocBtn: false,
    deleteDocActive: false,
    deleteDocMessage: '',
    currentDeleteDocId: null,
    currentDeleteDocName: null,
    types_documents_list: null,
    showUploadDocsDialog: false,
    type_document: null,
    documentFiles: null,
    documentFileName: null,
    documents: [],
    affaireReadonly: true,
    dossier_affaire: null,
  }),

  methods: {
    /**
     * Search affaire dossier
     */
    async searchAffaireDossier() {
      this.$http.get(
        process.env.VUE_APP_API_URL + 
        process.env.VUE_APP_AFFAIRE_DOSSIER_ENDPOINT +
        this.$route.params.id,
        {
          withCredentials: true,
          headers: {Accept: "application/json"}
        }
      ).then(response => {
        if (response && response.data) {
          this.dossier_affaire = response.data;
        }
      }).catch(err => handleException(err, this))
    },

    /*
     * SEARCH AFFAIRE DOCUMENTS
     */
    async searchAffaireDocuments() {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_DOCUMENTS_ENDPOINT +
            this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            this.documents = response.data;
          }
        })
        .catch(err => {
          handleException(err, this);
        });

        this.showUploadDocsDialog = false;
    },

    /**
     * Télécharger le document en local
     */
    downloadItem(item) {
      axios.get(item.chemin.replace(/\\/g, "/"), { responseType: "blob" })
        .then(response => {
          const blob = new Blob([response.data], { type: "application/pdf" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          window.open(link.href)
        })
        .catch(console.error);
    },

    /*
    * Init types clients list
    */
    initTypesDocumentsList() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_TYPES_DOCUMENTS_ENDPOINT,
        {
          withCredentials: true,
          headers: {"Accept": "application/json"}
        }
      )
      .then(response =>{
        if (response && response.data) {
          this.types_documents_list = response.data;

          if(this.types_documents_list.length > 0){
            this.type_document = this.types_documents_list[0].id;
          }
        }
      })
      //Error 
      .catch(err => {
        handleException(err, this);
      });
    },

    /**
     * Upload affaire document to server
     */
    uploadAffaireDocument() {
      let _this = this;
      let formData = new FormData();
      
      for( var i = 0; i < this.documentFiles.length; i++ ){
        let file = this.documentFiles[i];

        formData.append('affaire_doc_files[' + i + ']', file);
      }

      //formData.append('affaire_doc_files', this.documentFiles);
      formData.append('affaire_id', this.$route.params.id);
      formData.append('type_id', this.type_document);

      axios.post(process.env.VUE_APP_API_URL +
          process.env.VUE_APP_AFFAIRE_UPLOAD_DOCUMENTS_ENDPOINT,
          formData, 
          {
              withCredentials: true,
              headers: {'Content-Type': 'multipart/form-data'}
          }
        ).then(function () {
         _this.$root.$emit("ShowMessage", "Le document " + _this.documentFilesName + " a été chargé avec succès");
         _this.searchAffaireDocuments();
        })
        .catch(function (err) {
          handleException(err, _this);
        });
    },

    /**
     * Handle file change
    */
    handleFileSelect(files) {
      if(files && files.length > 0){
        this.documentFiles = files;
      } 
    },
    
    /**
     * Download file
    */
    downloadFile(item) {
      const affaire_id = this.$route.params.id;
      window.open(process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_DOWNLOAD_DOCUMENT_ENDPOINT + '?affaire_id=' + affaire_id + '&filename=' + item.nom);
    },

    /**
     * Call delete document
     */
    callDeleteDoc (id, nom) {
      this.currentDeleteDocId = id;
      this.currentDeleteDocName = nom;
      this.deleteDocMessage = "Confirmer la suppression du document '<strong>" + nom + "<strong>' ?";
      this.deleteDocActive = true;
    },


    /**
    * Delete document
    */
    onConfirmDeleteDoc () {
       var formData = new FormData();
      formData.append("id", this.currentDeleteDocId);
      formData.append("nom", this.currentDeleteDocName);
      formData.append('affaire_id', this.$route.params.id);     

      this.$http
        .delete(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_DELETE_DOCUMENT_ENDPOINT,
          { 
            data: formData,
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response.data) {
            this.searchAffaireDocuments();
          }
        })
        .catch(err => {
          handleException(err, this);
        });

        this.currentDeleteDocId = null;
    },

    /**
    * Cancel delete document
    */
    onCancelDeleteDoc () {
      this.currentDeleteId = null;
    },

    /**
     * Copier dans le presse-papier
     */
    copyToClipboard () {
      // let copyText = document.querySelector(this.dossier_affaire);
      let copyText = document.querySelector("#dossier-affaire");
      copyText.setAttribute('type', 'text');
      copyText.select();
      var success = document.execCommand("copy");
      if (success) {
        this.$root.$emit("ShowMessage", "Copié dans le presse-papier avec succès")
      } else {
        this.$root.$emit("ErrorMessage", "Erreur, n'a pas pu copier le contenu")
      }
    }
  },

  mounted: function() {
    this.searchAffaireDocuments();
    this.initTypesDocumentsList();
    this.searchAffaireDossier();
    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_ENVOIS_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



