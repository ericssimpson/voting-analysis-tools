DROP TABLE IF EXISTS elections;

CREATE TABLE elections (
    state char(2),
    district_type varchar(30),
    district_id varchar(30),
    PRIMARY KEY (state, district_type, district_id)
);
