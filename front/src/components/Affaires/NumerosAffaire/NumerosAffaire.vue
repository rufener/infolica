<style src="./numerosAffaire.css" scoped></style>
<template src="./numerosAffaire.html"></template>


<script>
import { handleException } from "@/services/exceptionsHandler";
import { getCurrentDate, checkPermission } from "@/services/helper";
import ReferenceNumeros from "@/components/ReferenceNumeros/ReferenceNumeros.vue";
import ReservationNumeros from "@/components/ReservationNumeros/ReservationNumeros.vue";
import QuittancePCOP from "@/components/Affaires/NumerosAffaire/QuittancePCOP/QuittancePCOP.vue";
import Balance from "@/components/Affaires/Balance/Balance.vue";


const moment = require("moment");

export default {
  name: "NumerosAffaire",
  props: {
    affaire: Object,
    typesAffaires: Object
  },
  components: {
    ReferenceNumeros,
    ReservationNumeros,
    QuittancePCOP,
    Balance
  },
  data: () => {
    return {
      affaire_id: null,
      affaire_numeros_all: [],
      affaire_numeros_anciens: [],
      affaire_numeros_nouveaux: [],
      affaire_numeros_nouveaux_mo: [],
      affaireReadonly: true,
      showNumerosMO: true,
      numerosMoLoading: true,
      showBalance: false,
      showQuittancePCOPDialog: false,
      types_numeros: {
        bf: Number(process.env.VUE_APP_NUMERO_TYPE_BF),
        ddp: Number(process.env.VUE_APP_NUMERO_TYPE_DDP),
        ppe: Number(process.env.VUE_APP_NUMERO_TYPE_PPE),
        pcop: Number(process.env.VUE_APP_NUMERO_TYPE_PCOP)
      }
      // numeros_base_relations: []
    };
  },

  methods: {
    /*
     * SEARCH AFFAIRE NUMEROS
     */
    async searchAffaireNumeros() {
      return new Promise((resolve, reject) => {

        this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT +
            this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          const routeAffaireData = this.$router.resolve({ name: "Affaires" });

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
              } else if (element.numero_etat_id === Number(process.env.VUE_APP_NUMERO_PROJET_ID)) {
                element.active = true;
              }
            });

            //Affaires links
            this.affaire_numeros_anciens.map( function(item) {
              item.affaire_destination_href = routeAffaireData.href + '/' + item.affaire_destination_id;
              return item;
            });

            this.affaire_numeros_nouveaux.map( function(item) {
              item.affaire_destination_href = routeAffaireData.href + '/' + item.affaire_destination_id;
              return item;
            });

            resolve(this.affaire_numeros_all, this.affaire_numeros_anciens, this.affaire_numeros_nouveaux)
          }
        })
        .catch(err => {
          handleException(err, this);
          reject;
        });
      })
    },


    /**
     * Charger les réservations des numéros de la MO
     */
    async searchAffaireNewNumerosMo() {
      this.$http.get(
        process.env.VUE_APP_API_URL +
        process.env.VUE_APP_AFFAIRE_NEW_NUMEROS_MO_ENDPOINT +
        this.$route.params.id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.affaire_numeros_nouveaux_mo = response.data;
        }
      }).catch(err => {
        handleException(err, this)
      })
      this.numerosMoLoading = false;
    },


    /**
     * Contrôler qu'un numéro de référence n'est pas une numéro de base pour un numéro
     * réservé dans l'affaire
     */
    isNumeroBaseInAffaire(numero) {
      // Filtrer les numéros de base
      var numerosAssocies = this.affaire_numeros_nouveaux.filter(x => {
        return parseInt(x.numero_base_id) == parseInt(numero.numero_id);
      });
      // Créer un array avec les numéros pour l'affichage du message
      var numerosAssociesArray = [];
      numerosAssocies.forEach(x => numerosAssociesArray.push(x.numero));
      // Empêcher la suppression si des numéros sont définis sur le numéro de base, supprimer sinon
      if (numerosAssocies[0]) {
        this.$root.$emit(
          "ShowError",
          "Les immeubles " +
            numerosAssociesArray.join() +
            " sont définis sur l'immeuble " +
            numero.numero
        );
        return true;
      } else {
        return false;
      }
    },

    /**
     * Supprimer numéro référencé
     */
    onDeleteReferenceNumero(numero) {
      // Contrôler qu'aucun numéro n'a été défini sur ce numéro de base!
      if (this.isNumeroBaseInAffaire(numero) === false) {
        this.$http
          .delete(
            process.env.VUE_APP_API_URL +
              process.env.VUE_APP_REFERENCE_NUMEROS_ENDPOINT +
              "?affaire_id=" +
              this.$route.params.id +
              "&numero_id=" +
              numero.numero_id,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
          .then(response => {
            if (response.data) {
              this.searchAffaireNumeros();
              this.$root.$emit(
                "ShowMessage",
                "Le numéro " +
                  numero.numero +
                  " a été délié de l'affaire avec succès"
              );
            }
          })
          .catch(err => {
            handleException(err, this);
          });
      }
    },

    /**
     * Abandonner/rétablir un numéro réservé
     */
    onDeleteReserveNumero(numero_id) {
      // get numéro pour l'update
      var numero_ = {};
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_ENDPOINT +
            numero_id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response.data) {
            numero_ = response.data;
            this.updateNumero(numero_);
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Update Numero
     */
    async updateNumero(numero_) {
      this.$http
        .delete(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_ENDPOINT +
            numero_.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.status === 200) {
            this.searchAffaireNumeros();
            // Afficher le changement d'état
            var etat = "Abandonné";
            if (numero_.etat === "Abandonné") {
              etat = "Projet";
            }
            this.$root.$emit(
              "ShowMessage",
              "L'état du numéro " +
                numero_.numero +
                " est passé à '" +
                etat +
                "'"
            );
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Ouvrir la boîte de dialogue de référence de numéros
     */
    callOpenReferenceDialog() {
      this.$refs.formReference.openReferenceDialog();
    },

    /**
     * Ouvrir la boîte de dialogue de réservation de numéros
     */
    callOpenReservationDialog() {
      this.affaire_id = Number(this.$route.params.id);
      this.$refs.formReservation.openReservationDialog();
    },

    /**
     * Ouvrir le dialog de quittance de réservation de PCOP
     */
    callOpenQuittancePCOPDialog() {
      this.$refs.formQuittancePCOP.openQuittancePCOPDialog();
    },

    /**
     * Créer Différer un numéro
     */
    doCreateDiffererNumero(numero) {
      var formData = new FormData();
      formData.append("numero_id", numero.numero_id);
      formData.append("affaire_id", this.$route.params.id)
      formData.append(
        "date_entree",
        moment(getCurrentDate(), process.env.VUE_APP_DATEFORMAT_CLIENT).format(
          process.env.VUE_APP_DATEFORMAT_WS
        )
      );

      this.$http
        .post(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_DIFFERES_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            this.searchAffaireNumeros();
            this.$root.$emit(
              "ShowMessage",
              "Le numéro " + numero.numero + " a été différé"
            );
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Mettre à jour Différer un numéro
     */
    doUpdateDiffererNumero(numero) {
      var formData = new FormData();
      formData.append("numero_diff_id", numero.numero_diff_id);
      formData.append("numero_id", numero.numero_id);
      formData.append("date_entree", numero.numero_diff_entree);
      formData.append(
        "date_sortie",
        moment(getCurrentDate(), process.env.VUE_APP_DATEFORMAT_CLIENT).format(
          process.env.VUE_APP_DATEFORMAT_WS
        )
      );

      this.$http
        .put(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_DIFFERES_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            this.searchAffaireNumeros();
            this.$root.$emit(
              "ShowMessage",
              "La mention 'différé' du numéro " +
                numero.numero +
                " a été correctement supprimée"
            );
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    // /**
    //  * Get immeubles associes
    //  */
    // async getImmeublesAssocies() {
    //   return new Promise((resolve, reject) => {
    //     // Récupère la liste des id des numéros référencés
    //     var numeros_base_id_list = this.affaire_numeros_anciens.map(x => x.numero_id);
  
    //     var formData = new FormData();
    //     formData.append("numeros_base_id_list", JSON.stringify(numeros_base_id_list));
  
    //     this.$http.post(
    //       process.env.VUE_APP_API_URL +
    //       process.env.VUE_APP_NUMEROS_RELATIONS_BY_NUMEROSBASEID_ENDPOINT,
    //       formData,
    //       {
    //         withCredentials: true,
    //         headers: {'Content-type': 'application/json'},
    //       }
    //     )
    //     .then(response => {if (response && response.data) resolve(response.data)})
    //     .catch(err => reject(err));
    //   });
    // },

    /**
     * Afficher la balance si c'est une affaire de division
     */
    async showBalance_() {
      this.showBalance = await this.affaire.type_id === Number(process.env.VUE_APP_TYPE_AFFAIRE_DIVISION);
    }

  },
  mounted: function() {
    this.searchAffaireNumeros();
    this.searchAffaireNewNumerosMo();
    this.showBalance_();

    this.$root.$on('UpdateNumerosAffaires', () =>{
      this.searchAffaireNumeros();
    });
    
    this.affaireReadonly = !checkPermission(process.env.VUE_APP_AFFAIRE_NUMERO_EDITION) || this.$parent.parentAffaireReadOnly;
  }
};
</script>



