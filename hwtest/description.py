from hwtest.command import Command


class Description(Command):

    def __str__(self):
        return self.get_data()

    def get_command(self):
        command = super(Description, self).get_command()
        return "cat <<EOF\n%s\nEOF\n" % command

    def get_variables(self):
        variables = super(Description, self).get_variables()
        return {"output": variables["question"].command.get_data().strip()}
