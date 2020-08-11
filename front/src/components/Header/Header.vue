<style src="./header.css" scoped></style>
<template src="./header.html"></template>


<script>
export default {
  name: 'Header',
  props: {},

  data: function () {
      return {
          loggedUserName: String
      }
  },

  methods:{

    /**
     * Set user name
     */
    setUserName(data){
      if(data && data.nom && data.prenom)
        this.loggedUserName = data.prenom + ' ' + data.nom;

      else
        this.loggedUserName = null;
    },

    /**
     * call logout
     */
    callLogout(){
      if(this.$router && this.$router.currentRoute && this.$router.currentRoute.name != 'Login'){
        let vm = this;
        this.$router.push({name: "Login"}, function(){
          vm.$root.$emit("infolica_user_logout");
        });        
      }
      
    },

     /**
     * Go to route
     */
    goTo(route){
      if(this.$router && this.$router.currentRoute && this.$router.currentRoute.name != route)
        this.$router.push({ name: route});
    }
  },

  mounted: function(){
      //this.userNameVisible = false;

      this.$root.$on('infolica_user_logged_in', (logged_user) =>{
        this.setUserName(logged_user);
      });

      this.$root.$on('infolica_user_logged_out', () =>{
        this.setUserName(null);
      });

      var session_user = JSON.parse(localStorage.getItem('infolica_user')) || null;
      this.setUserName(session_user);
  }
}
</script>

