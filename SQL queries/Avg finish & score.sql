select player_name, avg(finish) as "avg_finish", avg(score) as "avg_score", count(finish) as "num_finishes"
from master
where year = 2024
and created_at >= '2024-02-15'
and finish is not null
and score is not null
group by player_name
order by avg_finish;

select *
from master
where year = 2024
and created_at >= '2024-02-15'
and finish is not null
and score is not null
and player_name = 'Scottie Scheffler'
order by id desc;

select * from master order by id desc;