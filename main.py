import src.main.DataAnalysHandler.DataAnalysHandler as DAH


def main():
    input_file_path = "C:/Users/eureka/Downloads/测速数据收集 (7).xlsx"
    output_file_path = "D:/pyproj/st/src/output"
    module_base_path = ""
    dah = DAH.DataAnalysHandler(input_file_path, output_file_path)
    dah.execute(input_file_path, output_file_path)

if __name__ == "__main__":
    main()