<style src="./preavisExternesEditDecision.css"></style>
<template src="./preavisExternesEditDecision.html"></template>


<script>
import { handleException } from "@/services/exceptionsHandler";
import PreavisExtComment from "@/components/Utils/PreavisExtComment/PreavisExtComment.vue";
import PreavisExternesEditOtherPreavis from "@/components/PreavisExternes/PreavisExternesEditOtherPreavis.vue";


export default {
  name: "PreavisEditDecision",
  props: {
    preavis_id: Number,
    showAddDecision: Boolean,
    affaire_id: Number,
  },
  components: {
    PreavisExtComment,
    PreavisExternesEditOtherPreavis,
  },
  data() {
    return {
      decisions_liste: [],
      decision: {
        id: null,
        preavis_type_id: null,
        remarque_contexte: null,
        remarque_limite_fictive_gabarits: null,
        remarque_transfert_droit_batir: null,
        remarque_stationnement_art29: null,
        remarque_autre: null,
        disabled: true,
        show: false,
      },
      glossaire: [],
      hasRightAddDecision: false,
      lastDecisionVersion: -1,
    };
  },

  methods: {
    /**
     * open new decision
     */
    openNewDecision() {
      this.resetDecision();
      this.decision.disabled = null;
      this.decision.show = true;
      this.getGlossaire();

    },


    // reset decision
    resetDecision() {
      this.decision.preavis_type_id = null;
      this.decision.remarque_contexte = null;
      this.decision.remarque_limite_fictive_gabarits = null;
      this.decision.remarque_transfert_droit_batir = null;
      this.decision.remarque_stationnement_art29 = null;
      this.decision.remarque_autre = null;
      this.decision.operateur = null;
      this.decision.date = null;
    },


    // get Decision List for menu
    async getDecisionList() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_DECISION_LIST_BY_PREAVIS_ID_ENDPOINT + "?preavis_id=" + this.preavis_id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.decisions_liste = response.data;

          //get max version of decision
          this.decisions_liste.forEach(x => {
            this.lastDecisionVersion = x.version > this.lastDecisionVersion? x.version: this.lastDecisionVersion;
          });

          this.decisions_liste.forEach(x => {
            if (x.preavis_type_id === 1) {
              x.icon_status = 'check_circle_outline';
              x.icon_status_style = x.version === this.lastDecisionVersion? 'color: green;': 'color: lightgrey; font-style: italic;';
            } else if (x.preavis_type_id === 2) {
              x.icon_status = 'highlight_off';
              x.icon_status_style = x.version === this.lastDecisionVersion? 'color: red;': 'color: lightgrey; font-style: italic;';
            } else if (x.preavis_type_id === 3) {
              x.icon_status = 'remove_circle_outline';
              x.icon_status_style = x.version === this.lastDecisionVersion? 'color: grey;': 'color: lightgrey; font-style: italic;';
            } else if (x.preavis_type_id === 5) {
              x.icon_status = 'error_outline';
              x.icon_status_style = x.version === this.lastDecisionVersion? 'color: orange;': 'color: lightgrey; font-style: italic;';
            }
          });
        }
      }
      ).catch(err => handleException(err, this));
    },



    // get Decision draft
    async getDecisionDraft() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_DECISION_BY_PREAVIS_ID_ENDPOINT + "?preavis_id=" + this.preavis_id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.decision = response.data;
          this.decision.show = true;
        }
        this.$root.$emit('setPreavisDecisionDraft');
      }
      ).catch(err => handleException(err))
      .finally(() => this.getGlossaire());
    },


    // saveDecision
    async saveDecision(definitif=false) {
      let formData = new FormData();
      formData.append('preavis_id', this.preavis_id);
      formData.append('preavis_type_id', this.decision.preavis_type_id);
      formData.append('remarque_contexte', this.decision.remarque_contexte);
      formData.append('remarque_limite_fictive_gabarits', this.decision.remarque_limite_fictive_gabarits);
      formData.append('remarque_transfert_droit_batir', this.decision.remarque_transfert_droit_batir);
      formData.append('remarque_stationnement_art29', this.decision.remarque_stationnement_art29);
      formData.append('remarque_autre', this.decision.remarque_autre);
      formData.append('definitif', definitif);

      return new Promise((resolve, reject) => {
        let req = this.$http
        if (this.decision.id) {
          formData.append('preavis_decision_id', this.decision.id)
          req = req.put(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_DECISION_BY_PREAVIS_ID_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
        } else {
          req = req.post(process.env.VUE_APP_API_URL + process.env.VUE_APP_PREAVIS_DECISION_BY_PREAVIS_ID_ENDPOINT,
            formData,
            {
              withCredentials: true,
              headers: { Accept: "application/json" }
            }
          )
        }

        req.then((response) => resolve(response)
        ).catch(err => reject(err));
      });
    },

    // save data provisoires
    async saveDecisionProvisoire() {
      this.saveDecision(false).then(() => {
        this.getDecisionDraft();
        this.$root.$emit('ShowMessage', 'La décision provisoire a bien été enregistrée');
      }).catch(err => handleException(err, this));
    },

    // get permissions
    getPermissions() {
      let session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;
      if (session_user && session_user.service_id) {
        this.hasRightAddDecision = true;
      }
    },

    // copy text from old preavis
    copyText(preavis) {
      this.decision.remarque_contexte = preavis.remarque_contexte;
      this.decision.remarque_limite_fictive_gabarits = preavis.remarque_limite_fictive_gabarits;
      this.decision.remarque_transfert_droit_batir = preavis.remarque_transfert_droit_batir;
      this.decision.remarque_stationnement_art29 = preavis.remarque_stationnement_art29;
      this.decision.remarque_autre = preavis.remarque_autre;
    },

    // get service glossaire
    async getGlossaire() {
      this.$http.get(process.env.VUE_APP_API_URL + process.env.VUE_APP_SERVICE_EXTERNE_GLOSSAIRE_ENDPOINT + "?preavis_id=" + this.preavis_id,
        {
          withCredentials: true,
          headers: { Accept: "application/json" }
        }
      ).then(response => {
        if (response && response.data) {
          this.glossaire = response.data;
        }
      }).catch(err => handleException(err));
    },
  },

  mounted: function() {
    this.getDecisionList();
    this.getDecisionDraft();
    this.getPermissions();
  }
};
</script>
