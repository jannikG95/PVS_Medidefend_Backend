import tiktoken


class CostService:
    #TODO: change costs_per_mille since currently there is no data for germany available ( the costs are swedish central )

    INPUT_COST_PER_MILLE = 0.01
    OUTPUT_COST_PER_MILLE = 0.029
    total_input_token_count = 0
    total_output_token_count = 0
    encoding = tiktoken.encoding_for_model('gpt-4')

    def add_io_tokens(self, prompt, response):
        self.add_input_tokens(prompt)
        self.add_output_tokens(response)

    def add_input_tokens(self, prompt):
        self.total_input_token_count += len(self.encoding.encode(prompt))

    def add_output_tokens(self, response):
        self.total_output_token_count += len(self.encoding.encode(response))

    def calculate_total_request_costs(self):
        input_total_costs = (self.total_input_token_count / 1000) * self.INPUT_COST_PER_MILLE
        output_total_costs = (self.total_output_token_count / 1000) * self.OUTPUT_COST_PER_MILLE

        return input_total_costs + output_total_costs

