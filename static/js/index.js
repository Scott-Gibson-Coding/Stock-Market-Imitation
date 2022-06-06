// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // sign up fields
        signup_email: "",
        signup_first_name: "",
        signup_last_name: "",
        signup_password: "",

        // flag indicating whether an email is valid or taken
        signup_email_valid: false,

        // errors
        signup_email_error: "",
        signup_first_name_error: "",
        signup_last_name_error: "",
        signup_password_error: "",
        signup_generic_error: "",

        // log in fields
        login_email: "",
        login_password: "",

        // errors
        login_email_error: "",
        login_password_error: "",
        login_generic_error: "", // in case of unexpected error
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // clear all error fields on signup/login attempt
    app.clear_error_fields = () => {
        app.vue.signup_email_error = "";
        app.vue.signup_first_name_error = "";
        app.vue.signup_last_name_error = "";
        app.vue.signup_password_error = "";
        app.vue.signup_generic_error = "";

        app.vue.login_email_error = "";
        app.vue.login_password_error = "";
        app.vue.login_generic_error = "";
    };

    // checks email syntax and returns a boolean
    app.check_email = (email) => {
        const re = /^.+@.+\..+$/;
        return email.match(re) ? email.match(re).length === 1 : false;
    };

    // check the signup email field if it's valid or if it's taken.
    app.check_signup_email = () => {
        app.vue.signup_email_error = "";
        app.vue.signup_email_valid = false;

        if (app.vue.signup_email === "") {
            return;
        }
        
        if (!app.check_email(app.vue.signup_email)) {
            // invalid syntax
            app.vue.signup_email_error = "Invalid Email Syntax";
        } else {
            // query database if email already exists
            axios.get(verify_email_url, {
                params: {
                    email: app.vue.signup_email
                }
            }).then(function (response) {
                let exists = response.data.exists;
                if (exists) {
                    app.vue.signup_email_error = "Email taken, please use a different one";
                } else {
                    app.vue.signup_email_valid = true;
                }
            });
        }
    };
    
    app.login = function() {
        app.clear_error_fields();
    
        if (app.vue.login_email != "" && app.vue.login_password != "") {
            if (app.check_email(app.vue.login_email)) {
                axios.post(login_url,
                    {
                        email: app.vue.login_email,
                        password: app.vue.login_password,
                    }
                ).then(function (response) {
                    console.log('login attempt successful');

                    // init user in db.user table
                    axios.get(init_user_url).then(function (response) {
                        console.log(response)
                    }).catch(function (error) {
                        console.log(error);
                    });

                    // reload index page
                    window.location = index_url;
                }).catch(function (error) {
                    console.log('an error occured');
                    if (error.response) {
                        error_msg = error.response.data.message;
                        console.log(error.response.data.message);
                        if (error_msg === 'Invalid email') {
                            app.vue.login_email_error = "Unregistered Email";
                        } else if (error_msg === 'Invalid Credentials') {
                            app.vue.login_password_error = 'Wrong Password';
                        } else {
                            app.vue.login_generic_error = "An Error Occured!";
                        }
                    } else {
                        app.vue.login_generic_error = "An Error Occured!";
                    }
                });
            } else {
                app.vue.login_email_error = "Invalid Email Syntax";
            }
        }
        if (app.vue.login_email === "") {
            app.vue.login_email_error = "Please fill out this field!";
        }
        if (app.vue.login_password === "") {
            app.vue.login_password_error = "Please fill out this field!";
        }
    };

    app.signup = function(props) {
        app.clear_error_fields();

        if (app.vue.signup_email != "" && app.vue.signup_first_name != ""
            && app.vue.signup_last_name != "" && app.vue.signup_password != "") {

            if (app.check_email(app.vue.signup_email)) {
                axios.post(signup_url,
                    {
                        email: app.vue.signup_email,
                        first_name: app.vue.signup_first_name,
                        last_name: app.vue.signup_last_name,
                        password: app.vue.signup_password,
                    }
                ).then(function (response) {
                    console.log('sign up attempt successful');
                    app.vue.login_email = app.vue.signup_email;
                    app.vue.login_password = app.vue.signup_password;
                    app.login();
                }).catch(function (error) {
                    console.log('an error occured');
                    if (error.response) {
                        error_code = error.response.data.code;
                        console.log(error_code)
                        if (error_code === 401) {
                            app.vue.signup_email_error = "Email taken, please use a different one";
                        } else {
                            app.vue.signup_generic_error = "An Error Occured!";
                        }
                    } else {
                        app.vue.signup_generic_error = "An Error Occured!";
                    }
                });
            } else {
                app.vue.signup_email_error = "Invalid Email Syntax";
            }
        }
        if (app.vue.signup_email === "") {
            app.vue.signup_email_error = "Please fill out this field";
        }
        if (app.vue.signup_first_name === "") {
            app.vue.signup_first_name_error = "Please fill out this field";
        }
        if (app.vue.signup_last_name === "") {
            app.vue.signup_last_name_error = "Please fill out this field";
        }
        if (app.vue.signup_password === "") {
            app.vue.signup_password_error = "Please fill out this field";
        }
    };

    // This contains all the methods
    app.methods = {
        login: app.login,
        signup: app.signup,
        check_signup_email: app.check_signup_email,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Put here any initialization code
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);