// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        comment_list: [],
        current_user_name: "",
        current_user_email: "",
        current_comment: "",
        adding_comment: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.complete = (a) => {
        // Add reactivity elements
        a.map((e) => {
            //e.reaction = 0;
            e.adding_reply = false;
            e.current_reply = "";
            e.show_replies = false;
            e.confirm_delete = false;
        });
        return a
    };

    app.complete_local_comment = (c) => {
        // Add reactivity elements
        c.likes = 0;
        c.dislikes = 0;
        c.replies = 0;
        c.reply_list = [];
    };

    app.complete_replies = (a) => {
        a.map((r)=> {
            r.confirm_delete = false;
        });
    };

    app.start_comment = function(){
        // Open field
        app.vue.adding_comment = true;
    };

    app.cancel_comment = function(){
        // Clear input field and hide comment
        app.vue.adding_comment = false;
        app.vue.current_comment = "";
    };

    app.post_comment = function(){
        // Send the comment to the server if not empty
        if (app.vue.current_comment != ""){
            let original_text = app.vue.current_comment;
            axios.post(post_comment_url, {'comment_text' : original_text, 'parent_idx': -1}
            ).then(function(response){
                // Add to reactive list
                //console.log(response.data);
                let new_comment = Object.assign({}, response.data);
                delete new_comment.flash;
                new_comment.comment = original_text;
                // Add reactive variables to the new post
                app.complete([new_comment]);
                app.complete_local_comment(new_comment);
                // Place at front of list and redo indices
                app.vue.comment_list.unshift(new_comment);
                app.enumerate(app.vue.comment_list);
                app.cancel_comment();
            });
        }
    };

    app.delete_comment = function(comment_idx){
        let comment = app.vue.comment_list[comment_idx];
        if (comment.confirm_delete){
            app.vue.comment_list.splice(comment_idx, 1)[0];
            app.enumerate(app.vue.comment_list);
            axios.get(delete_comment_url, {'params':{'comment_id':comment.id}});
        } else{
            comment.confirm_delete = true;
        }    
    };

    app.react = function(comment_idx, react){
        let comment = app.vue.comment_list[comment_idx];
        // Change the reaction state
        if (react === 'up'){
            if (comment.reaction === 1){
                comment.reaction = 0;
                comment.likes--;
            } else{
                if (comment.reaction === -1){
                    comment.dislikes--;
                }
                comment.reaction = 1;
                comment.likes++;
            }
        } else if (react === 'down'){
            if (comment.reaction === -1){
                comment.reaction = 0;
                comment.dislikes--;
            } else{
                if (comment.reaction === 1){
                    comment.likes--;
                }
                comment.reaction = -1;
                comment.dislikes++;
            }
        }
        // Save the new reaction to the db
        axios.post(save_reaction_url, 
            {'comment_id' : comment.id, 'reaction' : comment.reaction}
        );
    };

    app.start_reply = function(comment_idx){
        let comment = app.vue.comment_list[comment_idx];
        comment.adding_reply = true;
    };

    app.cancel_reply = function(comment_idx){
        let comment = app.vue.comment_list[comment_idx];
        comment.adding_reply = false;
        comment.current_reply = "";
    };

    app.post_reply = function(comment_idx){
        // Send the comment to the server if not empty
        let comment = app.vue.comment_list[comment_idx];
        if (comment.current_reply != ""){
            let original_text = comment.current_reply;
            axios.post(post_comment_url, {'comment_text' : original_text, 'parent_idx':comment.id}
            ).then(function(response){
                // Add to reactive list
                let new_comment = Object.assign({}, response.data);
                delete new_comment.flash;
                new_comment.comment = original_text;
                // Add reactive variables to the new post
                new_comment['likes'] = 0;
                new_comment['dislikes'] = 0;
                new_comment['confirm_delete'] = false;
                app.cancel_reply(comment_idx);
                // Place at back of list and redo indices
                comment.reply_list.push(new_comment);
                app.enumerate(comment.reply_list);
            });
        }
    };

    app.display_replies = function(comment_idx){
        let comment = app.vue.comment_list[comment_idx];
        comment.show_replies = true;
    };

    app.hide_replies = function(comment_idx){
        let comment = app.vue.comment_list[comment_idx];
        comment.show_replies = false;
    };

    app.delete_reply = function(comment_idx, reply_idx){
        let comment = app.vue.comment_list[comment_idx];
        let reply = comment.reply_list[reply_idx];
        if (reply.confirm_delete){
            comment.reply_list.splice(reply_idx, 1)[0];
            app.enumerate(comment.reply_list);
            axios.get(delete_comment_url, {'params':{'comment_id':reply.id}});
        }else{
            reply.confirm_delete = true;
        }
    };

    app.react_reply = function(comment_idx, reply_idx, react){
        let comment = app.vue.comment_list[comment_idx];
        let reply = comment.reply_list[reply_idx];
        // Change the reaction state
        if (react === 'up'){
            if (reply.reaction === 1){
                reply.reaction = 0;
                reply.likes--;
            } else{
                if (reply.reaction === -1){
                    reply.dislikes--;
                }
                reply.reaction = 1;
                reply.likes++;
            }
        } else if (react === 'down'){
            if (reply.reaction === -1){
                reply.reaction = 0;
                reply.dislikes--;
            } else{
                if (reply.reaction === 1){
                    reply.likes--;
                }
                reply.reaction = -1;
                reply.dislikes++;
            }
        }
        // Save the new reaction to the db
        axios.post(save_reaction_url, 
            {'comment_id' : reply.id, 'reaction' : reply.reaction}
        );
    };

    // This contains all the methods
    app.methods = {
        start_comment: app.start_comment,
        cancel_comment: app.cancel_comment,
        post_comment: app.post_comment,
        delete_comment: app.delete_comment,
        react: app.react,
        start_reply: app.start_reply,
        cancel_reply: app.cancel_reply,
        post_reply : app.post_reply,
        display_replies : app.display_replies,
        hide_replies : app.hide_replies,
        delete_reply : app.delete_reply,
        react_reply : app.react_reply,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Get the comments for the current post
        // as well as the post details
        axios.get(get_comments_url).then(function(response){
            // Save the comments
            let comments = response.data.comments;
            app.enumerate(comments);
            for (let c of comments){
                app.enumerate(c.reply_list);
                app.complete_replies(c.reply_list);
            }
            app.complete(comments);
            app.vue.comment_list = comments;
            // Save current user name and email
            app.vue.current_user_name = response.data.current_user_name;
            app.vue.current_user_email = response.data.current_user_email;
        });
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);