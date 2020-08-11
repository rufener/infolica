<style src="./reservationNumeros.css" scoped></style>
<template src="./reservationNumeros.html"></template>


<script>
import { getCadastres, stringifyAutocomplete } from "@/services/helper";
import { handleException } from "@/services/exceptionsHandler";
import { validationMixin } from "vuelidate";
import { required, minValue } from "vuelidate/lib/validators";

export default {
  name: "ReservationNumeros",
  props: {
    affaire: {type: Object},
    typesAffaires: {type: Object},
    types_numeros: {type: Object}
  },
  components: {},
  mixins: [validationMixin],
  data: () => {
    return {
      affaire_numeros_base: {
        DDP: null,
        PPE: null,
        PCOP: null
      },
      alertReservation: {
        show: false,
        saveReservation: false,
        text: ''
      },
      cadastre_liste: [],
      form: {
        cadastre: null,
        nombre: null,
        type_id: null,
        numeroBase: null,
        ppe_suffixe_start: null
      },
      numerosBaseListe: [],
      numerosBaseListeFiltered: [],
      showReservationDialog: false
    };
  },

  // Validations
  validations() {
    var form = {
      cadastre: { required },
      nombre: { 
        required,
        minValue: minValue(1)
      }
    };

    if (this.affaire.type_id === this.typesAffaires.ppe || this.affaire.type_id === this.typesAffaires.pcop) {
      form.numeroBase = { required };
    }

    if (this.affaire.type_id === this.typesAffaires.ppe) {
      form.ppe_suffixe_start = { required };
    }

    return { form };
  },

  methods: {
    /*
     * Init Cadastres list
     */
    initCadastresList() {
      getCadastres()
        .then(response => {
          if (response && response.data) {
            this.cadastre_liste = stringifyAutocomplete(response.data);
          }
        })
        .catch(err => {
          handleException(err, this);
        });
    },

    /**
     * Open reservation numéros dialog
     */
    openReservationDialog() {
      this.initializeForm();
      this.getNumerosBase();
      this.showReservationDialog = true;
    },

    /**
     * Create numeros
     */
    saveReservationNumeros() {
      var formData = new FormData();
      formData.append("affaire_id", this.affaire.id);
      formData.append("nombre", this.form.nombre);
      formData.append("cadastre_id", this.form.cadastre.id);
      formData.append("etat_id", Number(process.env.VUE_APP_NUMERO_PROJET_ID));
      if ((this.affaire.type_id === this.typesAffaires.ppe || this.affaire.type_id === this.typesAffaires.pcop) && this.form.numeroBase !== null && this.form.numeroBase.id) {
        formData.append("numero_base_id", this.form.numeroBase.id);
      }
      if (this.affaire.type_id === this.typesAffaires.ppe && this.form.ppe_suffixe_start !== null) {
        formData.append("ppe_suffixe_start", this.form.ppe_suffixe_start);
      }
      
      //Type de numéro selon le type d'affaire
      if (this.affaire.type_id === this.typesAffaires.mutation) {
        this.form.type_id = Number(process.env.VUE_APP_NUMERO_TYPE_BF);
      } else {
        this.form.type_id = Number(this.affaire.reservation_numeros_types_id[0]);
      }
      formData.append("type_id", this.form.type_id);
      
      this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_RESERVATION_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {"Accept": "application/json"}
          }
        )
        .then(response => {
          if (response.data) {
            this.$parent.searchAffaireNumeros();
            this.$root.$emit("ShowMessage", "Le(s) numéro(s) réservé(s) ont été correctement rattaché(s) à l'affaire")
          }
        })
        .catch(err => {
          handleException(err, this);
        });
      // this.showReservationDialog = false;
      this.initializeForm();
    },

    /**
     * Annuler la réservation de uméros
     */
    onCancelReservationNumeros() {
      this.showReservationDialog = false;
      this.initializeForm();
    },

    /**
     * Initialise le formulaire de réservation de numéros
     */
    initializeForm() {
      this.form.cadastre = this.cadastre_liste.filter(x => x.id === this.affaire.cadastre_id).pop();
      this.form.nombre = 0;
      this.form.numeroBase = null;
      this.form.ppe_suffixe_start = null;
    },

    /**
     * Get validation class par fieldname
     */
    getValidationClass(fieldName) {
      const field = this.$v.form[fieldName];

      if (field) {
        return {
          "md-invalid": field.$invalid && field.$dirty
        };
      }
    },

    /**
     * Confirmer l'édition de la facture et l'enregistrer
     */
    onConfirmReservationNumeros() {
      
      this.$v.$touch();

      if (!this.$v.$invalid) {
        this.showReservationDialog = false;
      
        this.form.nombre = Number(this.form.nombre);
        if (this.form.nombre >= 10) {
          this.alertReservation.text = "En cliquant sur 'confirmer', " + this.form.nombre + " numéros de bien-fonds vont être réservés."
          this.alertReservation.show = true;
        } else {
          this.saveReservationNumeros();
        }
      }
    },

    /**
     * Retourne les numéros en vigueur et en projet dans le cadastre sélectionné
     */
    async getNumerosBase() {
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_ENDPOINT +
        "?cadastre_id=" + this.form.cadastre.id +
        "&type_id=" + process.env.VUE_APP_NUMERO_TYPE_BF + "," + process.env.VUE_APP_NUMERO_TYPE_DDP +
        "&etat_id=" + process.env.VUE_APP_NUMERO_PROJET_ID + "," +  process.env.VUE_APP_NUMERO_VIGUEUR_ID,
        {
          withCredentials: true,
          headers: {"Accept": "application/json"}
        }
      ).then(response => {
        if (response && response.data) {
          this.numerosBaseListe = stringifyAutocomplete(response.data, "numero");
          this.numerosBaseListeFiltered = this.numerosBaseListe.slice(0,20);
        }
      }).catch(err => handleException(err, this));
    },


    /**
     * Filter numero base in numero_base_liste
     */
    filterNumeroBase() {
      this.numerosBaseListeFiltered = this.numerosBaseListe;
      this.numerosBaseListeFiltered.filter(x => x.nom.includes(String(this.form.numeroBase))).slice(0,20);
    }
  },

  mounted: function() {
    this.initCadastresList();
  }
};
</script>

