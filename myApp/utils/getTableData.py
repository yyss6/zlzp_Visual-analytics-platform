from .getPublicData import getAllJobs
import json

def getTableData():
    jobs = getAllJobs()
    def map_fn(item):
        try:
            item.workTag = '/'.join(json.loads(item.workTag))
        except (json.JSONDecodeError, IndexError, TypeError, AttributeError):
            item.workTag = '' # Handle error, set to empty string or other default

        # Enhanced error handling for companyTags
        processed_company_tags = ''
        try:
            # Check if companyTags is not None and is a string before processing
            if item.companyTags and isinstance(item.companyTags, str) and item.companyTags.strip() != "无" and item.companyTags.strip() != "":
                 # Attempt to load JSON and split, handle errors
                 try:
                     company_tags_list = json.loads(item.companyTags)
                     # Ensure it's a list, has elements, and the first element is a non-empty string
                     if isinstance(company_tags_list, list) and len(company_tags_list) > 0 and isinstance(company_tags_list[0], str) and company_tags_list[0].strip() != "":
                         processed_company_tags = "/".join(company_tags_list[0].split('，'))
                     else:
                         # Handle unexpected JSON structure or empty string after loading
                         processed_company_tags = ''
                 except (json.JSONDecodeError, IndexError, AttributeError):
                     # Handle JSON parsing, index, or attribute errors during processing
                     processed_company_tags = ''
            else:
                # Handle None, non-string, "无", or empty string initially
                processed_company_tags = ''
        except Exception as e:
            # Catch any other unexpected errors during companyTags processing
            print(f"Error processing companyTags for job {item.id}: {e}")
            processed_company_tags = ''
        item.companyTags = processed_company_tags

        try:
            if item.companyPeople == '[0,10000]':
                item.companyPeople = '10000人以上'
            else:
                company_people_list = json.loads(item.companyPeople)
                if isinstance(company_people_list, list):
                    item.companyPeople = list(map(lambda x: str(x) + '人', company_people_list))
                    item.companyPeople = '-'.join(item.companyPeople)
                else:
                    item.companyPeople = '' # Handle unexpected JSON structure
        except (json.JSONDecodeError, AttributeError):
             item.companyPeople = '' # Handle JSON or attribute errors

        try:
             # Check if salary is not None and is a string before processing
             if item.salary and isinstance(item.salary, str):
                 salary_list = json.loads(item.salary)
                 if isinstance(salary_list, list) and len(salary_list) > 1:
                     # Ensure the second element is convertible to a number before assignment
                     try:
                         item.salary = float(salary_list[1]) # Assuming salary is [min, max]
                     except (ValueError, TypeError):
                         item.salary = 0 # Handle case where the second element is not a valid number
                 else:
                     item.salary = 0 # Handle unexpected JSON structure or not enough elements
             else:
                 item.salary = 0 # Handle None, non-string, or empty salary
        except (json.JSONDecodeError, IndexError, TypeError):
             item.salary = 0 # Handle JSON or index errors

        return item

    jobs = list(map(map_fn, jobs))
    return jobs

