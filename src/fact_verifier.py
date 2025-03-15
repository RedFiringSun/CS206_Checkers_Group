import requests
import json
import statistics
from datetime import datetime
from anthropic import Anthropic
import os

class ClaimBusterVerifier:
    def __init__(self, claimbuster_api_key, anthropic_api_key, output_file, json_output_file):
        # Initialize API credentials and endpoints
        self.claimbuster_api_key = claimbuster_api_key
        self.anthropic = Anthropic(api_key=anthropic_api_key)
        self.base_url = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
        self.headers = {"x-api-key": claimbuster_api_key}
        self.output_file = output_file
        self.json_output_file = json_output_file
        
        # Clear any existing content in the output file
        with open(self.output_file, 'w') as f:
            f.write("")
            
        with open(self.json_output_file, "w") as f:
            json.dump([], f, indent=2)      # Initialize with an empty JSON array
            
    def write_output(self, text):
        """Write text to output file"""
        with open(self.output_file, 'a') as f:
            f.write(text + '\n')
            
    def write_response_to_json(self, response_data, mode='a'):
        """Append the ClaimBuster API response to a JSON file as an array"""
        try:
            # Load existing JSON data (if any)
            if os.path.exists(self.json_output_file) and os.path.getsize(self.json_output_file) > 0:
                with open(self.json_output_file, "r") as f:
                    try:
                        existing_data = json.load(f)  # Read existing JSON
                        if not isinstance(existing_data, list):  # Ensure it's a list
                            existing_data = []
                    except json.JSONDecodeError:
                        existing_data = []  # Handle corrupted JSON case
            else:
                existing_data = []

            # Append new data
            existing_data.append(response_data)

            # Write back to the JSON file
            with open(self.json_output_file, "w") as f:
                json.dump(existing_data, f, indent=2)

        except Exception as e:
            print(f"Error writing to JSON file: {e}")   
        
    def get_claims(self, prompt, num_claims):
        """Get claims from a LLM"""
        try:
            # Construct prompt for the LLM
            system_prompt = f"Generate {num_claims} specific, verifiable factual claims about: {prompt}. Provide only the claims, one per line, without any headers or introductions."
            
            # Make API call
            message = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": system_prompt}]
            )

            # Example of LLM response
            """
            Here are 5 specific, verifiable factual claims about space exploration:
                1. The Apollo 11 mission landed the first humans on the Moon on July 20, 1969, with astronauts Neil Armstrong and Buzz Aldrin becoming the first humans to walk on the lunar surface while Michael Collins remained in orbit.
                2. The International Space Station (ISS) has been continuously occupied since November 2, 2000, with rotating crews from multiple countries, making it the longest continuous human presence in low Earth orbit.
                3. NASA's Voyager 1 spacecraft, launched in 1977, became the first human-made object to enter interstellar space in August 2012, traveling over 14.5 billion miles from Earth as of 2024.
                4. The Mars Curiosity rover, which landed on Mars on August 6, 2012, has discovered evidence of ancient lake environments and organic molecules in the Gale Crater, suggesting the planet once had conditions that could have supported microbial life.
                5. SpaceX's Falcon 9 rocket achieved the first successful ground landing of an orbital rocket's first stage on December 21, 2015, revolutionizing space technology by demonstrating reusable rocket technology and significantly reducing the cost of space launches.
            These claims are based on well-documented scientific and historical records from space agencies and research institutions.
            """
            
            # Result after processing
            """
            claims = [
                "The Apollo 11 mission landed the first humans on the Moon on July 20, 1969, with astronauts Neil Armstrong and Buzz Aldrin becoming the first humans to walk on the lunar surface while Michael Collins remained in orbit.",
                "The International Space Station (ISS) has been continuously occupied since November 2, 2000, with rotating crews from multiple countries, making it the longest continuous human presence in low Earth orbit.",
                "NASA's Voyager 1 spacecraft, launched in 1977, became the first human-made object to enter interstellar space in August 2012, traveling over 14.5 billion miles from Earth as of 2024.",
                "The Mars Curiosity rover, which landed on Mars on August 6, 2012, has discovered evidence of ancient lake environments and organic molecules in the Gale Crater, suggesting the planet once had conditions that could have supported microbial life.",
                "SpaceX's Falcon 9 rocket achieved the first successful ground landing of an orbital rocket's first stage on December 21, 2015, revolutionizing space technology by demonstrating reusable rocket technology and significantly reducing the cost of space launches."
            ]
            """
            
            # 1. Get the raw text and split into lines
            claims = message.content[0].text.strip().split('\n')
            
            # 2. Process each claim using list comprehension
            claims = [
                # Removes whitespace and specific characters from start of each claim
                claim.strip()                           # Remove whitespace from both ends
                    .lstrip('0123456789.)-[] ')         # Removes numbers, dots, brackets etc. from start
                    
                # Only keep claims that meet these conditions:
                for claim in claims                     # Process each claim in the list
                if claim.strip()                        # Claim must not be empty after stripping
                and not claim.lower().startswith(('here', 'following'))         # Claim must not start with these words
            ]
            
            # 3. Return only the requested number of claims
            return claims[:num_claims]
            
        except Exception as e:
            print(f"Claude API Error: {e}")
            return None

    def verify_claim(self, claim, topic, source="Claude-3-Haiku"):
        """Verify a single claim and track its topic"""
        try:
            # Make API call to ClaimBuster
            payload = {"input_text": claim}     # Formats claim to ClaimBuster API
            response = requests.post(           # Makes POST request to API
                url=self.base_url,              # Users stored API URL
                json=payload,                   # Sends claim as JSON
                headers=self.headers            # Includes API key in headers
            )
            response.raise_for_status()         # Checks for HTTP errors
            response_data = response.json()     # Converts API response to Python dict
            
            # What is stored in 'response_data' variable
            """
            {
                "version": "2",
                "claim": "The Apollo 11 mission landed...",
                "results": [                      # This is why we check for 'results'
                    {
                        "text": "The Apollo 11 mission landed...",
                        "index": 0,
                        "score": 0.6964           # This is why we use results[0]['score']
                    }
                ]
            }
            """
            self.write_response_to_json(response_data)

            # Checks if response is empty or missing 'results' field
            # Returns None if invalid
            if not response_data or 'results' not in response_data:
                print(f"Invalid response format: {response_data}")
                return None
                
            # Checks if 'results' is empty or not a list
            # Returns None if invalid
            if not response_data['results'] or not isinstance(response_data['results'], list):
                print(f"No results in response: {response_data}")
                return None
                
            # More specific error handling for score extraction
            try:
                # Get the score from the first result
                score = response_data['results'][0]['score']
            except (KeyError, IndexError) as e:
                print(f"Error extracting score from response: {e}")
                print(f"Response data: {response_data}")
                return None
            
            # Result creation
            verification_result = {
                'claim': claim,             # original claim text
                'score': score,             # factual confidence score
                'source': source,           # where claim came from
                'topic': topic,             # topic of claim
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),      # when verified
                'confidence_level': self._get_confidence_level(score),          # score interpretation
                'token_estimate': len(claim.split()) * 1.3                      # estimated tokens used
            }
            
            # Return result
            return verification_result
            
        # Handle any API or processing errors
        except requests.exceptions.RequestException as e:
            print(f"API Request Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during verification: {str(e)}")
            return None
    
    def _get_confidence_level(self, score):
        """Convert numerical score to confidence level"""
        if score >= 0.8:
            return "High factual confidence"
        elif score >= 0.6:
            return "Medium factual confidence"
        elif score >= 0.4:
            return "Low factual confidence"
        else:
            return "Very low factual confidence"

    def batch_verify_claims(self, topic, num_claims, max_retries=3):
        """Process multiple claims for a given topic"""
        
        # Get claims from a LLM
        claims = self.get_claims(topic, num_claims)
        if not claims:
            return []
            
        # Initialize tracking variables
        results = []            # stores a list of dictionaries
                                # each dictionary contains the verification for a single claim
                                        
        total_tokens = 0        # keeps track of number of tokens used
        failed_claims = 0       # keeps track of number of failed claims
        
        # Write topic header to output file
        self.write_output("\n" + "=" * 70)
        self.write_output(f"TOPIC: {topic.upper()}")
        self.write_output("=" * 70 + "\n")
        
        # Process each claim
        for i, claim in enumerate(claims, 1):
            # Skip empty claims
            if not claim.strip():
                continue
                
            result = None       # initialize results
            retries = 0         # initialize the number of retries
            
            # Retry verification up to max_retries times
            while result is None and retries < max_retries:
                if retries > 0:
                    self.write_output(f"Retrying verification for claim {i} (attempt {retries + 1})")
                result = self.verify_claim(claim, topic)
                retries += 1
                
            # Process successful verification
            if result:
                results.append(result)
                total_tokens += result['token_estimate']

                # Write claim details to output
                self.write_output(f"CLAIM {i - failed_claims}:")
                self.write_output(f"Text: {claim}")
                self.write_output(f"Factual Score: {result['score']:.4f}")
                self.write_output(f"Confidence Level: {result['confidence_level']}")
                self.write_output(f"Estimated Tokens: {result['token_estimate']:.0f}")
                self.write_output("")
            else:
                # Handle failed verification
                failed_claims += 1
                self.write_output(f"\nWarning: Failed to verify claim {i} after {max_retries} attempts:")
                self.write_output(f"Text: {claim}")
        
        if results:
            self.write_output("\nBatch Summary:")
            self.write_output("-" * 20)
            self.write_output(f"Total Tokens: {total_tokens:.0f}")
            self.write_output(f"Estimated Cost: ${(total_tokens / 1_000_000) * 1.33:.4f}")
            
        # Write warning for failed claims
        if failed_claims > 0:
            self.write_output(f"\nWarning: {failed_claims} claims failed verification\n")
        
        return results

    def generate_report(self, results, topic_info):
        """Generate a fact verification analysis report"""
        if not results:
            return "No results to analyze"
            
        # Extract all factual scores from results into a list
        scores = [r['score'] for r in results]
        
        # Build report header with topic info
        report = "\n" + "=" * 70 + "\n"
        report += f"FACT VERIFICATION REPORT: {topic_info.upper()}\n"
        report += "=" * 70 + "\n\n"
        
        # Add summary statistics section
        report += "Summary Statistics:\n"
        report += "-" * 20 + "\n"
        report += f"Total claims analyzed: {len(results)}\n"
        
        # Calculate and add statistical measures if we have scores
        if scores:
            report += f"Average factual score: {statistics.mean(scores):.4f}\n"
            report += f"Median factual score: {statistics.median(scores):.4f}\n"
            # Only calculate standard deviation if we have more than one score
            if len(scores) > 1:
                report += f"Std deviation: {statistics.stdev(scores):.4f}\n"
            report += f"Min score: {min(scores):.4f}\n"
            report += f"Max score: {max(scores):.4f}\n"
        
        # Add confidence level distribution section
        report += "\nConfidence Level Distribution:\n"
        report += "-" * 20 + "\n"
        
        # Count occurences of each confidence level
        confidence_dist = {}
        for result in results:
            conf = result['confidence_level']
            
            # Increment count for this confidence level (default to 0 if not seen before)
            confidence_dist[conf] = confidence_dist.get(conf, 0) + 1
            
        # Calculate and add percentage for each confidence level
        for conf, count in confidence_dist.items():
            percentage = (count / len(results)) * 100
            report += f"{conf}: {count} claims ({percentage:.1f}%)\n"

        # Add report footer
        report += "\n\n" + "/" * 100 + "\n"
        
        # Write report to output file
        self.write_output(report)
        
        # Return the generated report
        return report
    
def read_api_keys(key_file="key.txt"):
    """Read API keys from file"""
    try:
        with open(key_file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 2:
                claimbuster_key = lines[0].strip()
                anthropic_key = lines[1].strip()
                return claimbuster_key, anthropic_key
            else:
                raise ValueError("Key file must contain both ClaimBuster and Anthropic API keys")
    except FileNotFoundError:
        print(f"Error: {key_file} not found. Please create a file with your API keys")
        return None, None
    except Exception as e:
        print(f"Error reading API keys: {str(e)}")
        return None, None

def main():
    """Main execution function to run the fact verification process"""
    
    import anthropic
    print(f"requests=={requests.__version__}")
    print(f"anthropic=={anthropic.__version__}")
    
    # Read API Keys from file
    # key.txt should have ClaimBuster key on first line, Anthropic key on second line
    CLAIMBUSTER_API_KEY, ANTHROPIC_API_KEY = read_api_keys("key.txt")
    if not CLAIMBUSTER_API_KEY or not ANTHROPIC_API_KEY:
        print("Failed to read API keys. Exiting...")
        return
        
    # Define output file path where results will be written    
    OUTPUT_FILE = "fact_verification_output.txt"
    JSON_OUTPUT_FILE = "output.json"
    
    # Initialize verifier object with both APIs and output file
    verifier = ClaimBusterVerifier(CLAIMBUSTER_API_KEY, ANTHROPIC_API_KEY, OUTPUT_FILE, JSON_OUTPUT_FILE)

    # List of topics to generate and verify claims about
    topics = [
        "Science & Technology",
        "History & Politics",
        "Medicine & Health",
        "Environmental Science",
        "Business & Economics"
    ]

    # Store all verification results across topics
    all_results = []
    
    try:
        # Process each topic one by one
        for topic in topics:
            # Get claims from LLM and verify them with ClaimBuster
            results = verifier.batch_verify_claims(topic, num_claims=5)
            
            # If verification was successful, add results and generate report
            if results:
                all_results.extend(results)     # Add topic results to overall results
                verifier.generate_report(results, f"Claude-3-Haiku on {topic}")
        
        # After all topics processed, generate final statistics if we have results
        if all_results:
            # Calculate total tokens used across all claims
            total_tokens = sum(r['token_estimate'] for r in all_results)
            
            # Calculate total cost using Claude API rates:
            # Input cost: $0.80/million tokens
            # Output cost: $4.00/million tokens
            total_cost = (total_tokens / 1_000_000) * (0.80 + 4.00)
            
            # Write final statistics to output file
            verifier.write_output("\n" + "=" * 70)
            verifier.write_output("FINAL SESSION STATISTICS")
            verifier.write_output("=" * 70)
            verifier.write_output(f"\nTotal Claims Processed: {len(all_results)}")
            verifier.write_output(f"Total Estimated Tokens: {total_tokens:.0f}")
            verifier.write_output(f"Total Estimated Cost: ${total_cost:.4f}")
            
    # Catch and log any errors that occur during processing
    except Exception as e:
        verifier.write_output(f"\nError during processing: {str(e)}")

if __name__ == "__main__":
    main()