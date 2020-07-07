-- [params]
-- string :interval = 1 month
-- string :trunc = month

WITH timeperiod AS (
    SELECT date_trunc(:trunc, CURRENT_TIMESTAMP - INTERVAL :interval) as start,
    date_trunc(:trunc, CURRENT_TIMESTAMP) as end),

postsread AS (
    SELECT 
        user_id, 
        count(1) AS visits,
        sum(posts_read) AS posts_read
    FROM user_visits
    INNER JOIN timeperiod 
        ON visited_at >= timeperiod.start
        AND visited_at <= timeperiod.end
    WHERE posts_read > 0
    GROUP BY user_id),

solutions AS (
    SELECT 
        ua.user_id,
        count(1) AS solved_count
    FROM user_actions ua
    INNER JOIN timeperiod 
        ON ua.created_at >= timeperiod.start
        AND ua.created_at <= timeperiod.end
    INNER JOIN users ON users.id = ua.user_id
    WHERE ua.action_type = 15
/*  AND users.admin = 'f' AND users.moderator = 'f'*/
    GROUP BY ua.user_id ),

likes AS (
    SELECT 
        post_actions.user_id as given_by_user_id, 
        posts.user_id as received_by_user_id
    FROM posts 
    LEFT JOIN post_actions
        ON post_actions.post_id = posts.id
        AND post_action_type_id = 2
    INNER JOIN timeperiod 
        ON post_actions.created_at >= timeperiod.start
        AND post_actions.created_at <= timeperiod.end),

likesreceived AS (
    SELECT 
        received_by_user_id AS user_id, 
        count(1) AS likes_received
    FROM likes
    GROUP BY user_id),

emails AS (
    SELECT email, user_id FROM user_emails ue WHERE ue.primary = true),

replies AS (
    SELECT 
        posts.user_id, 
        count(posts.id) as replies
    FROM postsread 
    INNER JOIN posts
        ON postsread.user_id = posts.user_id 
    INNER JOIN timeperiod 
        ON posts.created_at >= timeperiod.start
        AND posts.created_at <= timeperiod.end
    WHERE posts.post_type = 1 
        AND posts.post_number > 1 
        AND posts.user_id > 0
        AND posts.topic_id NOT IN ('4','24','26','32','33','34','35','36','37','38','39','40')
    GROUP BY posts.user_id),
    
employee AS(SELECT user_id FROM group_users WHERE group_id = 41)

SELECT postsread.user_id,
       name,
       email,
       COALESCE(solved_count,0) AS solutions_prov, 
       COALESCE(likes_received,0) AS likes_recv,
       COALESCE(replies,0) AS replies_made,
       (
            (COALESCE(solved_count,0) * 3) +
            (COALESCE(replies,0) * 2) +
            (COALESCE(likes_received,0) * 1)
       ) AS total_points
FROM postsread
LEFT JOIN solutions USING (user_id)
LEFT JOIN likesreceived USING (user_id)
LEFT JOIN emails USING (user_id)
LEFT JOIN users u ON postsread.user_id = u.id
LEFT JOIN replies ON replies.user_id = u.id
WHERE postsread.user_id NOT IN (SELECT * FROM employee)  /*COMMENT THIS LINE TO INCLUDE EMPLOYEES*/
ORDER BY total_points DESC
