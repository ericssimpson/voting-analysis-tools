from os import path
import logging
import sqlite3 as sqlite

"""
Class for building database functionalities.
"""
class DB:
    def __init__(self, connection):
        self.conn = connection

    def execute_script(self, script_file):
        """
        Runs sql scripts when given the file name
        """
        with open(script_file, "r") as script:
            c = self.conn.cursor()
            c.executescript(script.read())
            self.conn.commit()

    def create_shapes_table(self):
        """
        Calls the schemas/shapes.sql file
        """
        script_file = path.join("schemas", "shapes.sql")
        self.execute_script(script_file)
    
    def create_elections_table(self):
        """
        Calls the schemas/elections.sql file
        """
        script_file = path.join("schemas", "elections.sql")
        self.execute_script(script_file)
