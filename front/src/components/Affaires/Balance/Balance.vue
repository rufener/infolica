<style src="./balance.css" scoped></style>
<template src="./balance.html"></template>

<script>
import { handleException } from "@/services/exceptionsHandler";
import { getTypesNumeros, getCadastres, stringifyAutocomplete } from "@/services/helper";
import moment from 'moment'

export default {
  name: "Balance",
  props: {
    affaire: { type: Object },
    affaire_numeros_all: { type: Array }
  },
  data: () => {
    return {
      // numeros_liste = [],
      cadastres_liste: [],
      numeros_anciens: [],
      numeros_nouveaux: [],
      numeros_relations: [],
      numeros_relations_bk: [],
      numeros_relations_matrice: [],
      numeros_types_liste: [],
      oldBF_toCreate: [],
      showConfirmationCreateNumber: false
    };
  },
  methods: {
    /**
     * Séparer les anciens numéros et les numéros projetés
     */
    initBFArrays() {
      this.numeros_anciens = this.affaire_numeros_all.filter(
        x =>
          x.affaire_numero_type_id ===
            Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID) &&
          x.numero_type_id === Number(process.env.VUE_APP_NUMERO_TYPE_BF)
      );

      this.numeros_nouveaux = this.affaire_numeros_all.filter(
        x =>
          x.affaire_numero_type_id ===
            Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_NOUVEAU_ID) &&
          x.numero_type_id === Number(process.env.VUE_APP_NUMERO_TYPE_BF) &&
          x.numero_etat_id !== Number(process.env.VUE_APP_NUMERO_ABANDONNE_ID)
      );

      this.initTableRelation();
    },

// =============================================================

    /**
     * Init list of number types
     */
    async initNumeroTypes() {
      getTypesNumeros().then(response => {
        if (response && response.data) {
          this.numeros_types_liste = stringifyAutocomplete(response.data).filter(x => {
            return x.id === Number(process.env.VUE_APP_NUMERO_TYPE_BF) || x.id === Number(process.env.VUE_APP_NUMERO_TYPE_DDP)
          });
        }
      }).catch(err => handleException(err, this));
    },

    async initCadastres() {
      getCadastres().then(response => {
        if (response && response.data) {
          this.cadastres_liste = stringifyAutocomplete(response.data);
        }
      }).catch(err => handleException(err, this));
    },

    /**
     * Get balance from file
     */
    async getBalanceFromFile() {
      // Get balance from file via webservice
      this.$http.get(
        process.env.VUE_APP_API_URL + process.env.VUE_APP_BALANCE_ENDPOINT + this.$route.params.id,
        {
          withCredentials: true,
          headers: {Accept: "application/json"}
        }
      ).then(response => {
        if (response && response.data){
          let tmp = JSON.parse(response.data);

          // Get old and new BF
          let oldBF = [];
          let newBF = [];

          tmp.forEach(x => {
            oldBF.push(x.old);
            newBF.push(x.new);
          });

          // Only keep unique BF
          oldBF = [...new Set(oldBF)];
          newBF = [...new Set(newBF)];

          // Check if oldBF are existing numbers
          let promises = [];
          oldBF.forEach(number => {
            promises.push(this.checkOldBF(number, this.affaire.cadastre_id, Number(process.env.VUE_APP_NUMERO_TYPE_BF))); // ================== !!! cadastre_id peut être différent !!
          })

          this.oldBF_toCreate = [];
          this.numeros_anciens = [];

          Promise.all(promises).then(responses => {
            responses.forEach(response => {
              if (response && response.data && response.data[0]) {
                this.numeros_anciens = {
                  id: response.data.id,
                  numero: response.data.numero
                }
              } else {
                const url = new URL(response.config.url)
                const numero = Number(url.searchParams.get("numero"));
                const cadastre_id = Number(url.searchParams.get("cadastre_id"));
                const type_id = Number(url.searchParams.get("type_id"));
                
                this.oldBF_toCreate.push({
                    numero: numero,
                    cadastre: this.cadastres_liste.filter(x => x.id === cadastre_id).pop(),
                    type: this.numeros_types_liste.filter(x => x.id === type_id).pop()
                });
              }
            });
            
            // Ask the userconfirmation to create numbers that does not exist
            if (this.oldBF_toCreate[0]) {
              this.showConfirmationCreateNumber = true
            }
          }).catch(err => handleException(err, this));
          
          this.numeros_relations = tmp;
        }
      }).catch(err => handleException(err, this));
    },

    /**
     * Check existing old bf
     */
    async checkOldBF(numero, cadastre_id, type_id) {
      return new Promise((resolve, reject) => {
        this.$http.get(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_ENDPOINT +
          "?numero=" + numero + "&cadastre_id=" + cadastre_id + "&type_id=" + type_id,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      });
    },

    /**
     * Create old BF found in balance
     */
    async onCreateOldBF() {
      this.oldBF_toCreate.forEach(x => {
        this.postNumero(x)
        .then(() => this.showConfirmationCreateNumber = false)
        .catch(err => handleException(err, this));
      });
    },

    /**
     * Create numero
     */
    async postNumero(numero) {
      return new Promise((resolve, reject) => {
        let formData = new FormData();
        formData.append("numero", numero.numero);
        formData.append("cadastre_id", numero.cadastre.id);
        formData.append("type_id", numero.type.id);
        formData.append("etat_id", Number(process.env.VUE_APP_NUMERO_VIGUEUR_ID));

        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept : "application/json"}
          }
        ).then(response => {
          if (response && response.data) {
            const numero_id = Number(response.data)
            this.postNumeroAffaire(numero_id);
            this.postNumeroHistory(numero_id);
          }
          resolve(response);
        })
        .catch(err => reject(err));
      })
    },

    /**
     * Create link between affaire and numero
     */
    async postNumeroAffaire(numero_id) {
      return new Promise((resolve) => {
        let formData = new FormData();
        formData.append("affaire_id", this.affaire.id);
        formData.append("numero_id", numero_id);
        formData.append("type_id", Number(process.env.VUE_APP_AFFAIRE_NUMERO_TYPE_ANCIEN_ID));
        formData.append("actif", true);

        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_AFFAIRE_NUMEROS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept : "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => handleException(err, this));
      });
    },

    /**
     * Create history of new number
     */
    async postNumeroHistory(numero_id) {
      return new Promise((resolve) => {
        let formData = new FormData();
        formData.append("numero_id", numero_id);
        formData.append("numero_etat_id", Number(process.env.VUE_APP_NUMERO_VIGUEUR_ID));
        formData.append("date", moment(new Date()).format(process.env.VUE_APP_DATEFORMAT_WS));

        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_ETAT_HISTO_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept : "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => handleException(err, this));
      });
    },

    /**
     * Post numero_relation
     */
    async postNumerosRelations(numero_id_base, numero_id_associe) {
      return new Promise((resolve, reject) => {
        let formData = new FormData();
        formData.append("numero_id_base", numero_id_base);
        formData.append("numero_id_associe", numero_id_associe);
        formData.append("relation_type_id", Number(process.env.VUE_APP_RELATION_TYPE_MUTATION_ID));
        formData.append("affaire_id", this.affaire.id);

        this.$http.post(
          process.env.VUE_APP_API_URL + process.env.VUE_APP_NUMEROS_RELATIONS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept : "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      });
    },







    // =======================================================


    /**
     * Initialiser la table des relations
     */
    initTableRelation() {
      // 1. retourne les relations
      this.getNumerosRelations()
      .then(response => {
        this.numeros_relations = response;
        this.numeros_relations_bk = response

      // 2. construire la matrice des relations
      this.numeros_relations_matrice = [];

      this.numeros_anciens.forEach(x => {
        var tmp_nouveaux = {};

        this.numeros_nouveaux.forEach(y => {
          var tmp = false;
          tmp = this.numeros_relations.some(rel => {
            if (rel.source_numero_id === x.numero_id && rel.destination_numero_id === y.numero_id) {
              return true
            } else {
              return false
            }
          })
          if (tmp) {
            tmp_nouveaux[y.numero] = true;
          } else {
            tmp_nouveaux[y.numero] = false;
          }
        });

        this.numeros_relations_matrice.push({
          source_numero: x.numero,
          source_numero_id: x.numero_id,
          destination: Object.assign({}, tmp_nouveaux)
        });
      });
    })
    .catch(err => handleException(err, this));
    },

    /**
     * Update variable numeros_relations
     */
    updateNumerosRelations() {
      this.numeros_relations = [];

      var tmp = [];
      this.numeros_relations_matrice.forEach(num_ancien => {
        let keys_ = Object.keys(num_ancien.destination); // keys_ = nouveaux numéros
        keys_.forEach(key_ => {
          if (num_ancien.destination[key_] === true) {
            let destination_numero_id = this.getNumeroId(
              key_, // nouveau numéro
              this.numeros_nouveaux // liste des nouveaux numéros
            );

            var relation_id = this.numeros_relations_bk.find(rel_bk => {
              return rel_bk.source_numero_id === num_ancien.source_numero_id && rel_bk.destination_numero_id === destination_numero_id
            })
            if (relation_id) {
              relation_id = relation_id.relation_id;
            } else {
              relation_id = null
            }

            tmp.push({
              relation_id: relation_id,
              source_numero: num_ancien.source_numero,
              source_numero_id: num_ancien.source_numero_id,
              destination_numero: key_,
              destination_numero_id: destination_numero_id
            });
          }
        });
      });
      this.numeros_relations = tmp;
    },

    /**
     * Recherche du numero_id à partir du numero
     */
    getNumeroId(numero_, liste_numeros) {
      const result = liste_numeros.filter(
        x =>
          x.numero === Number(numero_)
      );
      return result[0].numero_id;
    },

    /**
     * Get balance (numeros_relations)
     */
    async getNumerosRelations() {
      return new Promise((resolve, reject) => {
      this.$http
        .get(
          process.env.VUE_APP_API_URL +
            process.env.VUE_APP_NUMEROS_RELATIONS_BY_AFFAIREID_ENDPOINT +
            this.$route.params.id,
          {
            withCredentials: true,
            headers: { Accept: "application/json" }
          }
        )
        .then(response => {
          if (response && response.data) {
            let numeros_relations = response.data
              .filter(x =>
                x.numero_relation_type_id === Number(process.env.VUE_APP_RELATION_TYPE_MUTATION_ID)
              )
              .map(x => ({
                relation_id: x.numero_relation_id,
                source_numero_id: x.numero_base_id,
                source_numero: x.numero_base,
                destination_numero_id: x.numero_associe_id,
                destination_numero: x.numero_associe
              }));
            resolve(numeros_relations);
          }
        })
        .catch(err => reject(err));
      })
    },

    /**
     * Save new balance
     */
    saveBalance() {
      // Ajouter les relations qui ont été établies
      let relations_id = []; // enregistrer une liste des ID des relations existantes dans la BD
      let promises = [];
      this.numeros_relations.forEach(rel => {
        if (rel.relation_id) {
          relations_id.push(rel.relation_id);
        } else {
          // Si la relation est nouvelle (i.e. n'existe pas dans la BD)
          promises.push(this.postRelation(rel));
        }
      });

      // Supprimer les relations qui n'existent plus
      this.numeros_relations_bk.forEach(rel => {
        if (!relations_id.includes(rel.relation_id)) {
          promises.push(this.deleteRelation(rel));
        }
      })
    
      Promise.all(promises)
      .then(() => {
        this.$root.$emit("ShowMessage", "La balance a bien été mise à jour")
      })
      .catch(err => handleException(err, this));
    },

    /**
     * Create relation in db
     */
    async postRelation(rel) {
      var formData = new FormData();
      formData.append("numero_id_base", rel.source_numero_id);
      formData.append("numero_id_associe", rel.destination_numero_id);
      formData.append("relation_type_id", process.env.VUE_APP_RELATION_TYPE_MUTATION_ID); 
      formData.append("affaire_id", this.$route.params.id);
      
      return new Promise((resolve, reject) => {
        this.$http.post(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_RELATIONS_ENDPOINT,
          formData,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      })
    },


    /**
     * Delete relation in db
     */
    async deleteRelation(rel) {
      return new Promise((resolve, reject) => {
        this.$http.delete(
          process.env.VUE_APP_API_URL +
          process.env.VUE_APP_NUMEROS_RELATIONS_ENDPOINT + "?numero_relation_id=" +  rel.relation_id,
          {
            withCredentials: true,
            headers: {Accept: "application/json"}
          }
        ).then(response => resolve(response))
        .catch(err => reject(err));
      })
    },


  },
  mounted: function() {
    this.getNumerosRelations();
    this.initNumeroTypes();
    this.initCadastres();
  }
};
</script>
