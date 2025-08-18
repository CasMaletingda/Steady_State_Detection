from steady_detect.io_utils import load_data
from steady_detect.plotting import plot_all
from steady_detect.export import write_plots_excel

def main():
    df = load_data("data.xlsx")
    plots = plot_all(df)
    out_path = write_plots_excel(plots)
    print("已完成：", out_path)

if __name__ == "__main__":
    main()
