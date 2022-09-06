from os import path

project_path = path.abspath("..")
exp_t2d_path = path.abspath(path.join("../exp_T2D"))
exp_limaye_path = path.abspath(path.join("../exp_Limaye"))
limaye_path = path.abspath(path.join("../Limaye"))
t2dv2_path = path.abspath(path.join("../T2Dv2"))

Word2Wec_path = path.abspath(path.join("../w2v_model/enwiki_model/"))

if __name__ == '__main__':
    print(project_path)
    print(exp_limaye_path)
    print(exp_t2d_path)
    print(t2dv2_path)
    print(limaye_path)
    print(Word2Wec_path)