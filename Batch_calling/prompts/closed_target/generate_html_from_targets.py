from targets import target_list

def generate_taxonomy(targets, stance_types, stances):
    """
    Generate Label Studio taxonomy XML for stance classification with customizable parameters
    
    Args:
        targets (list): List of target names
        stance_types (list): List of stance types (e.g., EXPLICIT, IMPLICIT)
        stances (list): List of possible stances (e.g., FAVOR, AGAINST)
        
    Returns:
        str: XML string for Label Studio taxonomy
    """
    xml = '<Taxonomy name="taxonomy" toName="text" showFullPath="true" pathSeparator=" → ">\n'
    
    for target in targets:
        # Add target
        xml += f'  <Choice value="{target}">\n'
        
        # Add stance types
        for stance_type in stance_types:
            xml += f'    <Choice value="{stance_type}">\n'
            
            # Add stances for each stance type
            for stance in stances:
                xml += f'      <Choice value="{stance}"/>\n'
            
            # Close stance type choice
            xml += '    </Choice>\n'
        
        # Close target choice
        xml += '  </Choice>\n'
    
    xml += '</Taxonomy>'
    return xml


# Define stance types and stances (easily modifiable)
stance_types = ["EXPLICIT", "IMPLICIT"]
stances = ["FAVOR", "AGAINST", "NONE"]

# Generate the taxonomy
taxonomy_xml = generate_taxonomy(target_list, stance_types, stances)

# Print the result
print(taxonomy_xml)

# # Save to a file
# with open('taxonomy.xml', 'w') as f:
#     f.write(taxonomy_xml)

# # Additionally, generate a complete Label Studio configuration
# complete_config = f'''<View>
#   <!-- The text to analyze -->
#   <Text name="text" value="$prompt"/>
  
#   <!-- Instructions -->
#   <Header name="instructions_header" value="Stance Classification Instructions"/>
#   <Text name="instructions_text" value="1. Select targets mentioned in the text&#10;2. For each target, navigate to the appropriate stance type ({', '.join(stance_types)})&#10;3. Then select the stance ({', '.join(stances)})&#10;4. Provide the key claim for FAVOR or AGAINST stances in the text area below" />
  
#   <!-- Taxonomy for targets with nested stance types and stances -->
#   {taxonomy_xml}
  
#   <!-- Filter for finding targets -->
#   <Filter name="taxonomy_filter" toName="taxonomy" hotkey="shift+f" minlength="1" placeholder="Filter targets..."/>
  
#   <!-- Key claim input -->
#   <Header name="key_claim_header" value="Key claim (only provide for FAVOR or AGAINST stances)"/>
#   <TextArea name="key_claim" toName="text" 
#            value="I agree with the following: "
#            placeholder="Complete the claim here..."
#            rows="3" editable="true"/>
# </View>'''

# # Save the complete configuration
# with open('label_studio_config.xml', 'w') as f:
#     f.write(complete_config)

# print("\nComplete Label Studio configuration saved to 'label_studio_config.xml'")