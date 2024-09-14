DROP TABLE IF EXISTS shapes;

CREATE TABLE shapes (
    state char(2),
    district_type varchar(30),
    district_id varchar(30),
    PRIMARY KEY (state, district_type, district_id)
);

